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
from datetime import datetime, timedelta, timezone

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.growth import attribution
from app.growth.business_data import BusinessSnapshot, cached_snapshot
from app.growth.meta_delivery import PERMANENT, backoff_for, classify
from app.integrations.connectors.meta_connector import MetaConnector, MetaVerificationError
from app.integrations.gateway.factory import get_connector_gateway
from app.models.growth import STATUS_PROCESSED, GrowthEvent
from app.models.meta_conversion import (
    STATUS_PERMANENT_FAILURE,
    STATUS_QUEUED,
    STATUS_RETRY,
    STATUS_SENDING,
    STATUS_SENT,
    MetaConversion,
)

logger = logging.getLogger("colore.meta_sync")

BATCH_SIZE = 100

MAX_EVENT_AGE_SECONDS = 7 * 24 * 3600
"""Meta: "If any event_time in data is greater than 7 days in the past, we
return an error for the entire request and process no events."

One stale event therefore poisons every event it travels with. They are taken
out of the queue before a batch is assembled rather than discovered by having a
batch rejected."""


@dataclass
class SyncResult:
    built: int = 0
    sent: int = 0
    accepted: int = 0
    retry: int = 0
    permanent_failure: int = 0
    expired: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def rejected(self) -> int:
        """Anything that did not get through, whatever happens to it next."""
        return self.retry + self.permanent_failure


@dataclass
class MetaStatus:
    connected: bool = False
    missing: list[str] = field(default_factory=list)
    waiting: int = 0
    sent: int = 0
    accepted: int = 0
    rejected: int = 0
    retry: int = 0
    permanent_failure: int = 0
    last_sync: datetime | None = None
    errors: list[str] = field(default_factory=list)
    by_outcome: dict[str, int] = field(default_factory=dict)
    failure_reasons: dict[str, int] = field(default_factory=dict)

    # Scheduler view — answers "is anything actually going to send this?"
    scheduler_running: bool | None = None
    job_registered: bool = False
    last_run_at: datetime | None = None
    last_run_status: str = ""
    next_run_at: datetime | None = None
    last_success_at: datetime | None = None
    last_error: str = ""
    last_error_at: datetime | None = None

    # Salon profile and target, so the report answers "what is this configured
    # against" without exposing a single secret.
    salon_name: str = ""
    salon_country: str = ""
    salon_timezone: str = ""
    currency: str = ""
    dataset_id: str = ""


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
                status=STATUS_QUEUED,
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


def _payload_for(row: MetaConversion) -> dict:
    event = {
        "event_name": row.event_name,
        "event_time": row.event_time,
        "event_id": row.event_id,
        "action_source": row.action_source,
        "user_data": attribution.json.loads(row.user_data or "{}"),
    }
    if row.custom_data:
        event["custom_data"] = attribution.json.loads(row.custom_data)
    return event


def expire_stale(session: Session, *, now: float | None = None) -> int:
    """Take events past Meta's 7-day window out of the queue, before batching.

    They can never be accepted, and one of them travelling in a batch causes
    Meta to reject every event alongside it. Removing them here is the
    difference between losing one unsendable event and losing ninety-nine
    sendable ones.
    """
    now = now if now is not None else datetime.now(timezone.utc).timestamp()
    cutoff = int(now - MAX_EVENT_AGE_SECONDS)

    stale = (
        session.query(MetaConversion)
        .filter(
            MetaConversion.status.in_((STATUS_QUEUED, STATUS_RETRY)),
            MetaConversion.event_time < cutoff,
        )
        .all()
    )

    for row in stale:
        row.status = STATUS_PERMANENT_FAILURE
        row.error = (
            "event_time is more than 7 days in the past — Meta rejects the "
            "whole request if any event is older than that, so this one is "
            "never sent"
        )
        row.next_attempt_at = None

    if stale:
        session.commit()

    return len(stale)


def _mark_sent(rows: list[MetaConversion], response: dict, now: datetime) -> None:
    body = attribution.dumps(response)
    for row in rows:
        row.attempts += 1
        row.status = STATUS_SENT
        row.response = body[:2000]
        row.error = ""
        row.sent_at = now
        row.next_attempt_at = None


def _mark_retry(rows: list[MetaConversion], reason: str, now: datetime) -> None:
    for row in rows:
        row.attempts += 1
        row.status = STATUS_RETRY
        row.error = reason
        row.next_attempt_at = now + timedelta(seconds=backoff_for(row.attempts))


def _mark_permanent(row: MetaConversion, reason: str, now: datetime) -> None:
    row.attempts += 1
    row.status = STATUS_PERMANENT_FAILURE
    row.error = reason
    row.sent_at = now
    row.next_attempt_at = None


def eligible_rows(session: Session, *, limit: int = BATCH_SIZE, now: datetime | None = None):
    """Rows that would be sent right now. Shared by the sender and by dry runs,
    so a dry run reports on exactly what a real run would touch."""
    now = now or datetime.utcnow()
    return (
        session.query(MetaConversion)
        .filter(
            MetaConversion.status.in_((STATUS_QUEUED, STATUS_RETRY, STATUS_SENDING)),
            or_(
                MetaConversion.next_attempt_at.is_(None),
                MetaConversion.next_attempt_at <= now,
            ),
        )
        .order_by(MetaConversion.id)
        .limit(limit)
        .all()
    )


def _send_batch(
    connector,
    session: Session,
    rows: list[MetaConversion],
    result: SyncResult,
    *,
    test_event_code: str | None = None,
) -> None:
    """Send a batch, isolating a bad event rather than condemning its neighbours.

    Meta answers per request, not per event, so a permanent rejection does not
    say which event caused it. Rather than assume all of them are bad — the
    behaviour this change exists to remove — the batch is halved and each half
    retried until the offender is alone and identifiable. That costs at most
    2·log₂(n) extra requests and never discards a good event.
    """
    if not rows:
        return

    now = datetime.utcnow()

    try:
        response = connector.send_conversions(
            [_payload_for(row) for row in rows],
            test_event_code=test_event_code,
        )
    except Exception as exc:  # noqa: BLE001 — classified, never swallowed
        kind, reason = classify(exc)

        if kind != PERMANENT:
            _mark_retry(rows, f"{reason}: {exc}", now)
            result.retry += len(rows)
            result.errors.append(f"{reason} — {len(rows)} event(s) will be retried")
            session.commit()
            return

        if len(rows) == 1:
            _mark_permanent(rows[0], f"{reason}: {exc}", now)
            result.permanent_failure += 1
            result.errors.append(f"event {rows[0].event_id}: {reason}")
            session.commit()
            return

        # More than one event and a permanent answer: split to find the culprit.
        middle = len(rows) // 2
        _send_batch(connector, session, rows[:middle], result, test_event_code=test_event_code)
        _send_batch(connector, session, rows[middle:], result, test_event_code=test_event_code)
        return

    _mark_sent(rows, response, now)
    result.sent += len(rows)
    result.accepted += len(rows)
    session.commit()


def send_pending(
    session: Session,
    *,
    limit: int = BATCH_SIZE,
    test_event_code: str | None = None,
) -> SyncResult:
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

    result.expired = expire_stale(session)

    due = eligible_rows(session, limit=limit)
    if not due:
        return result

    # Claim the rows so a crash mid-send is recoverable: `sending` rows are
    # picked up again on the next run rather than sitting invisible.
    for row in due:
        row.status = STATUS_SENDING
    session.commit()

    _send_batch(connector, session, due, result, test_event_code=test_event_code)
    return result


def synchronise(session: Session, *, days: int = 90) -> SyncResult:
    built, errors = build_queue(session, days=days)
    result = send_pending(session)
    result.built = built
    result.errors = errors + result.errors
    return result


# ----------------------------------------------------------------- scheduler


def _scheduler_service_active() -> bool | None:
    """Whether the host scheduler unit is running. None when it cannot be told."""
    import subprocess

    try:
        proc = subprocess.run(
            ["systemctl", "is-active", "colore-scheduler"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception:  # noqa: BLE001 — no systemd inside a container
        return None
    return proc.stdout.strip() == "active"


def _read_scheduler_state(session: Session, status: MetaStatus) -> None:
    """Answer the question the Meta report could not previously answer: is
    anything going to send this, and when?"""
    from app.core.salon import salon_profile

    profile = salon_profile()
    status.salon_name = profile.name
    status.salon_country = profile.country
    status.salon_timezone = profile.timezone
    status.currency = profile.currency

    connector = _meta_connector()
    # The dataset id is an identifier, not a credential — Meta shows it in
    # Events Manager. Nothing else about the connector is exposed.
    status.dataset_id = connector.dataset_id if connector else ""

    status.scheduler_running = _scheduler_service_active()

    try:
        from app.growth.meta_job import JOB_NAME
        from app.scheduler.runner import build_service

        service = build_service()
        if JOB_NAME not in service.registry.names():
            return
        status.job_registered = True

        last = service.last_run(session, JOB_NAME)
        if last is not None:
            status.last_run_at = last.started_at
            status.last_run_status = last.status

        success = service.last_run(session, JOB_NAME, status="success")
        if success is not None:
            status.last_success_at = success.started_at

        failure = service.last_run(session, JOB_NAME, status="failed")
        if failure is not None:
            status.last_error = failure.error or failure.message
            status.last_error_at = failure.started_at

        status.next_run_at = service.next_run_at(session, service.registry.get(JOB_NAME))
    except Exception as exc:  # noqa: BLE001
        status.errors.append(f"scheduler state unavailable: {type(exc).__name__}: {exc}")


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

    _read_scheduler_state(session, status)

    try:
        rows = session.query(MetaConversion).all()
    except Exception as exc:  # noqa: BLE001
        status.errors.append(f"cannot read meta_conversions: {type(exc).__name__}")
        return status

    for row in rows:
        if row.status in (STATUS_QUEUED, STATUS_SENDING):
            status.waiting += 1
            status.by_outcome[row.outcome] = status.by_outcome.get(row.outcome, 0) + 1
        elif row.status == STATUS_RETRY:
            # Still in the queue — it has not been given up on.
            status.waiting += 1
            status.retry += 1
            status.rejected += 1
            status.by_outcome[row.outcome] = status.by_outcome.get(row.outcome, 0) + 1
            if row.error:
                key = row.error[:80]
                status.failure_reasons[key] = status.failure_reasons.get(key, 0) + 1
        elif row.status == STATUS_SENT:
            status.sent += 1
            status.accepted += 1
        elif row.status == STATUS_PERMANENT_FAILURE:
            status.permanent_failure += 1
            status.rejected += 1
            if row.error:
                key = row.error[:80]
                status.failure_reasons[key] = status.failure_reasons.get(key, 0) + 1

        if row.sent_at and (status.last_sync is None or row.sent_at > status.last_sync):
            status.last_sync = row.sent_at

    return status
