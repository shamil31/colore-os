"""The Growth AI pipeline: normalise, deduplicate, decide, dispatch, record.

    Meta → n8n → Coloré OS → Growth AI → Telegram

Every stage writes to the trace, including the stages that decide to do
nothing. "Nothing happened" is the hardest thing to debug in an integration,
so a skipped echo and a duplicate retry are both recorded facts here rather
than silence.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.growth.normalize import NormalisedEvent, SkippedEvent, normalise
from app.integrations.gateway import capabilities
from app.integrations.gateway.connector_gateway import ConnectorGateway
from app.models.growth import (
    STATUS_FAILED,
    STATUS_PROCESSED,
    STATUS_SKIPPED,
    GrowthAction,
    GrowthEvent,
)
from app.services.growth_ai import GrowthAI

logger = logging.getLogger("colore.growth")

MAX_RAW_CHARS = 20000


async def ingest(
    db: Session,
    payload: dict[str, Any],
    *,
    gateway: ConnectorGateway,
    growth_ai: GrowthAI,
) -> dict[str, Any]:
    outcome = normalise(payload)

    if isinstance(outcome, SkippedEvent):
        return _record_skip(db, outcome, payload)

    existing = (
        db.query(GrowthEvent)
        .filter(
            GrowthEvent.source == outcome.source,
            GrowthEvent.external_id == outcome.external_id,
        )
        .first()
    )
    if existing is not None:
        # Meta retries for 36 hours and says deduplication is our job. A repeat
        # is normal traffic, not an anomaly.
        return {
            "result": "duplicate",
            "event_id": existing.id,
            "source": existing.source,
            "external_id": existing.external_id,
        }

    event = GrowthEvent(
        source=outcome.source,
        external_id=outcome.external_id,
        sender_ref=outcome.sender_ref,
        sender_name=outcome.sender_name,
        channel_ref=outcome.channel_ref,
        text=outcome.text,
        raw=_dump(outcome.raw),
    )
    db.add(event)

    try:
        db.commit()
    except IntegrityError:
        # Two retries arrived at once and both passed the check above.
        db.rollback()
        duplicate = (
            db.query(GrowthEvent)
            .filter(
                GrowthEvent.source == outcome.source,
                GrowthEvent.external_id == outcome.external_id,
            )
            .first()
        )
        return {
            "result": "duplicate",
            "event_id": duplicate.id if duplicate else None,
            "source": outcome.source,
            "external_id": outcome.external_id,
        }

    db.refresh(event)

    decision = await growth_ai.decide(outcome)
    event.intent = decision.intent
    event.priority = decision.priority
    event.decision_reason = decision.reason

    result = gateway.dispatch(
        capabilities.MESSAGE_SEND,
        {"text": decision.alert_text},
    )

    db.add(
        GrowthAction(
            event_id=event.id,
            connector=result.connector,
            capability=result.capability,
            status=result.status,
            request=_dump(result.request),
            response=_dump(result.data),
            error=result.error or "",
        )
    )

    event.status = STATUS_PROCESSED if result.ok else STATUS_FAILED
    db.commit()
    db.refresh(event)

    return {
        "result": "processed",
        "event_id": event.id,
        "source": event.source,
        "external_id": event.external_id,
        "intent": event.intent,
        "priority": event.priority,
        "reason": event.decision_reason,
        "dispatch": {
            "connector": result.connector,
            "status": result.status,
            "error": result.error,
        },
    }


def _record_skip(
    db: Session,
    outcome: SkippedEvent,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Persist a skip when it can be identified, so it is greppable later."""
    if not outcome.external_id:
        logger.info("growth: skipped payload (%s: %s)", outcome.reason, outcome.detail)
        return {"result": "skipped", "reason": outcome.reason, "detail": outcome.detail}

    existing = (
        db.query(GrowthEvent)
        .filter(GrowthEvent.external_id == outcome.external_id)
        .first()
    )
    if existing is not None:
        return {"result": "duplicate", "event_id": existing.id, "reason": outcome.reason}

    event = GrowthEvent(
        source="meta",
        external_id=outcome.external_id,
        status=STATUS_SKIPPED,
        skip_reason=outcome.reason,
        decision_reason=outcome.detail,
        raw=_dump(payload),
    )
    db.add(event)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return {"result": "duplicate", "reason": outcome.reason}

    db.refresh(event)
    return {
        "result": "skipped",
        "event_id": event.id,
        "reason": outcome.reason,
        "detail": outcome.detail,
    }


def _dump(value: Any) -> str:
    if value is None:
        return ""
    try:
        text = json.dumps(value, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        text = str(value)
    return text[:MAX_RAW_CHARS]


def event_to_dict(event: GrowthEvent, actions: list[GrowthAction] | None = None) -> dict[str, Any]:
    data: dict[str, Any] = {
        "id": event.id,
        "source": event.source,
        "external_id": event.external_id,
        "sender_ref": event.sender_ref,
        "sender_name": event.sender_name,
        "text": event.text,
        "status": event.status,
        "skip_reason": event.skip_reason,
        "intent": event.intent,
        "priority": event.priority,
        "decision_reason": event.decision_reason,
        "received_at": event.received_at.isoformat() if event.received_at else None,
    }
    if actions is not None:
        data["actions"] = [
            {
                "id": action.id,
                "connector": action.connector,
                "capability": action.capability,
                "status": action.status,
                "error": action.error,
                "created_at": action.created_at.isoformat() if action.created_at else None,
            }
            for action in actions
        ]
    return data
