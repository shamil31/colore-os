"""The attribution queue: build from confirmed outcomes, send, record the answer.

Three separate steps, deliberately:

1. **Build.** Read confirmed outcomes and insert any that are not queued yet.
   Idempotent: `event_id` is derived from the source record, so rebuilding over
   the same data inserts nothing.
2. **Send.** Hand pending events to Meta, in batches.
3. **Record.** Mark each one accepted or rejected, keeping Meta's answer.

Build never sends, and send never invents. If Meta is not configured, step 1
still runs and the queue accumulates — so the moment credentials exist, the
history is already there rather than lost.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.growth import attribution
from app.growth.business_data import BusinessSnapshot, cached_snapshot
from app.integrations.connectors.meta_connector import MetaConnector, MetaVerificationError
from app.integrations.gateway.factory import get_connector_gateway
from app.models.growth import STATUS_PROCESSED, GrowthEvent
from app.models.meta_conversion import (
    STATUS_ACCEPTED,
    STATUS_PENDING,
    STATUS_REJECTED,
    MetaConversion,
)

logger = logging.getLogger("colore.meta_sync")

BATCH_SIZE = 100


@dataclass
class SyncResult:
    built: int = 0
    sent: int = 0
    accepted: int = 0
    rejected: int = 0
    errors: list[str] = field(default_factory=list)


@dataclass
class MetaStatus:
    connected: bool = False
    missing: list[str] = field(default_factory=list)
    waiting: int = 0
    sent: int = 0
    accepted: int = 0
    rejected: int = 0
    last_sync: datetime | None = None
    errors: list[str] = field(default_factory=list)
    by_outcome: dict[str, int] = field(default_factory=dict)


def _meta_connector() -> MetaConnector | None:
    try:
        connector = get_connector_gateway().integration_registry.get("meta")
    except KeyError:
        return None
    return connector if isinstance(connector, MetaConnector) else None


# --------------------------------------------------------------------- build


def build_queue(
    session: Session,
    *,
    days: int = 90,
    snapshot: BusinessSnapshot | None = None,
) -> tuple[int, list[str]]:
    """Insert events for outcomes that are confirmed and not queued yet."""
    errors: list[str] = []
    snapshot = snapshot if snapshot is not None else cached_snapshot(days=days)

    if not snapshot.connected:
        errors.extend(snapshot.errors or ["Altegio unavailable"])
        return 0, errors

    errors.extend(snapshot.errors)

    since = datetime.utcnow() - timedelta(days=days)
    leads = (
        session.query(GrowthEvent)
        .filter(
            GrowthEvent.status == STATUS_PROCESSED,
            GrowthEvent.received_at >= since,
        )
        .all()
    )

    events = attribution.build_events(snapshot, leads)
    if not events:
        return 0, errors

    known = {
        row[0]
        for row in session.query(MetaConversion.event_id)
        .filter(MetaConversion.event_id.in_([e.event_id for e in events]))
        .all()
    }

    inserted = 0
    for event in events:
        if event.event_id in known:
            continue

        session.add(
            MetaConversion(
                outcome=event.outcome,
                event_name=event.event_name,
                event_id=event.event_id,
                event_time=event.event_time,
                action_source=event.action_source,
                source_system=event.source_system,
                source_ref=event.source_ref,
                user_data=attribution.dumps(event.user_data),
                custom_data=attribution.dumps(event.custom_data) if event.custom_data else "",
                status=STATUS_PENDING,
            )
        )
        try:
            session.commit()
        except IntegrityError:
            # Another run queued it between the check and the insert.
            session.rollback()
            continue
        inserted += 1

    return inserted, errors


# ---------------------------------------------------------------------- send


def send_pending(session: Session, *, limit: int = BATCH_SIZE) -> SyncResult:
    result = SyncResult()

    connector = _meta_connector()
    if connector is None:
        result.errors.append("Meta connector is not registered")
        return result

    if not connector.can_send_conversions:
        result.errors.append(
            "not configured: " + ", ".join(connector.missing_conversion_settings())
        )
        return result

    pending = (
        session.query(MetaConversion)
        .filter(MetaConversion.status == STATUS_PENDING)
        .order_by(MetaConversion.id)
        .limit(limit)
        .all()
    )
    if not pending:
        return result

    payload = []
    for row in pending:
        event = {
            "event_name": row.event_name,
            "event_time": row.event_time,
            "event_id": row.event_id,
            "action_source": row.action_source,
            "user_data": attribution.json.loads(row.user_data or "{}"),
        }
        if row.custom_data:
            event["custom_data"] = attribution.json.loads(row.custom_data)
        payload.append(event)

    now = datetime.utcnow()

    try:
        response = connector.send_conversions(payload)
    except MetaVerificationError as exc:
        message = str(exc)
        for row in pending:
            row.attempts += 1
            row.status = STATUS_REJECTED
            row.error = message
            row.sent_at = now
        session.commit()
        result.sent = len(pending)
        result.rejected = len(pending)
        result.errors.append(message)
        return result

    body = attribution.dumps(response)
    for row in pending:
        row.attempts += 1
        row.status = STATUS_ACCEPTED
        row.response = body[:2000]
        row.error = ""
        row.sent_at = now

    session.commit()
    result.sent = len(pending)
    result.accepted = len(pending)
    return result


def synchronise(session: Session, *, days: int = 90) -> SyncResult:
    built, errors = build_queue(session, days=days)
    result = send_pending(session)
    result.built = built
    result.errors = errors + result.errors
    return result


# -------------------------------------------------------------------- status


def read_status(session: Session, *, days: int = 90, build: bool = True) -> MetaStatus:
    status = MetaStatus()

    connector = _meta_connector()
    if connector is None:
        status.missing = ["META connector is not registered"]
    else:
        status.connected = connector.can_send_conversions
        status.missing = list(connector.missing_conversion_settings())
        if not connector.verify_token:
            status.missing.append("META_VERIFY_TOKEN")
        if not connector.app_secret:
            status.missing.append("META_APP_SECRET")

    if build:
        try:
            _, errors = build_queue(session, days=days)
            status.errors.extend(errors)
        except Exception as exc:  # noqa: BLE001
            logger.exception("meta queue build failed")
            status.errors.append(f"queue build failed: {type(exc).__name__}: {exc}")

    try:
        rows = session.query(MetaConversion).all()
    except Exception as exc:  # noqa: BLE001
        status.errors.append(f"cannot read meta_conversions: {type(exc).__name__}")
        return status

    for row in rows:
        if row.status == STATUS_PENDING:
            status.waiting += 1
            status.by_outcome[row.outcome] = status.by_outcome.get(row.outcome, 0) + 1
        else:
            status.sent += 1
            if row.status == STATUS_ACCEPTED:
                status.accepted += 1
            elif row.status == STATUS_REJECTED:
                status.rejected += 1

        if row.sent_at and (status.last_sync is None or row.sent_at > status.last_sync):
            status.last_sync = row.sent_at

    return status
