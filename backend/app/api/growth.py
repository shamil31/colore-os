"""Growth AI HTTP surface.

Two ways in, and they are not the same trust boundary:

`POST /growth/events` is the n8n hop. n8n owns the Meta subscription today, so
this endpoint trusts a shared secret sent as a header, exactly as the n8n
Webhook/HTTP Request nodes' "Header auth" provides.

`POST /growth/webhook/meta` is the direct Meta path, kept working so the day we
move the subscription off n8n needs no design. It trusts nothing but an
`X-Hub-Signature-256` HMAC over the raw request body.

Port 8000 is published publicly, so neither path is open. An unset secret
disables the endpoint rather than opening it.
"""

from __future__ import annotations

import hmac
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.integrations.connectors.meta_connector import (
    MetaConnector,
    MetaVerificationError,
)
from app.integrations.gateway.factory import get_connector_gateway
from app.models.growth import GrowthAction, GrowthEvent
from app.services.growth_ai import GrowthAI
from app.services.growth_service import event_to_dict, ingest
from app.services.llm_service import LLMService

logger = logging.getLogger("colore.growth")

router = APIRouter(prefix="/growth", tags=["Growth AI"])

INBOUND_TOKEN_HEADER = "X-Colore-Token"


def _growth_ai() -> GrowthAI:
    # Without a key there is no classifier; Growth AI then routes everything to
    # the operator as UNKNOWN rather than failing.
    return GrowthAI(llm=LLMService() if settings.OPENAI_API_KEY else None)


def _meta_connector() -> MetaConnector:
    connector = get_connector_gateway().integration_registry.get("meta")
    assert isinstance(connector, MetaConnector)
    return connector


def require_inbound_token(request: Request) -> None:
    """Shared-secret auth for the n8n hop.

    Both containers sit on `colore-net`, but the backend also publishes :8000,
    so network position is not authentication here.
    """
    if not settings.GROWTH_INBOUND_SECRET:
        raise HTTPException(
            status_code=503,
            detail=(
                "GROWTH_INBOUND_SECRET is not configured — the inbound event "
                "endpoint is disabled rather than left open"
            ),
        )

    provided = request.headers.get(INBOUND_TOKEN_HEADER, "")
    if not hmac.compare_digest(provided, settings.GROWTH_INBOUND_SECRET):
        raise HTTPException(status_code=401, detail=f"invalid or missing {INBOUND_TOKEN_HEADER}")


@router.get("/integrations")
def integrations_status():
    """What is registered, what is configured, and who serves which capability."""
    return get_connector_gateway().status()


@router.post("/events")
async def receive_event(
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(require_inbound_token),
):
    """Inbound hop from n8n. Accepts a Meta payload, wrapped or bare."""
    try:
        payload = await request.json()
    except Exception:  # noqa: BLE001
        raise HTTPException(status_code=400, detail="body must be JSON")

    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="body must be a JSON object")

    return await ingest(db, payload, gateway=get_connector_gateway(), growth_ai=_growth_ai())


@router.get("/webhook/meta", response_class=PlainTextResponse)
def verify_meta_webhook(request: Request):
    """Meta's subscription handshake. Echoes hub.challenge verbatim."""
    params = request.query_params
    try:
        challenge = _meta_connector().verify_subscription(
            mode=params.get("hub.mode"),
            token=params.get("hub.verify_token"),
            challenge=params.get("hub.challenge"),
        )
    except MetaVerificationError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    return PlainTextResponse(challenge)


@router.post("/webhook/meta")
async def receive_meta_webhook(request: Request, db: Session = Depends(get_db)):
    """Direct Meta path, authenticated by signature over the raw body."""
    connector = _meta_connector()

    if not connector.can_verify_signatures:
        raise HTTPException(
            status_code=503,
            detail=(
                "META_APP_SECRET is not configured — the direct Meta webhook is "
                "disabled. Deliver through n8n (POST /growth/events) instead."
            ),
        )

    # Read the bytes Meta sent. Re-serialising the parsed JSON before checking
    # would break the signature on payloads that are semantically identical.
    raw_body = await request.body()

    try:
        connector.verify_signature(
            raw_body=raw_body,
            signature_header=request.headers.get("X-Hub-Signature-256"),
        )
    except MetaVerificationError as exc:
        logger.warning("growth: rejected Meta webhook: %s", exc)
        raise HTTPException(status_code=401, detail=str(exc))

    try:
        payload = await request.json()
    except Exception:  # noqa: BLE001
        raise HTTPException(status_code=400, detail="body must be JSON")

    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="body must be a JSON object")

    return await ingest(db, payload, gateway=get_connector_gateway(), growth_ai=_growth_ai())


@router.get("/events")
def list_events(limit: int = 50, db: Session = Depends(get_db)):
    """The trace. Newest first."""
    limit = max(1, min(limit, 200))
    events = (
        db.query(GrowthEvent)
        .order_by(GrowthEvent.id.desc())
        .limit(limit)
        .all()
    )
    return [event_to_dict(event) for event in events]


@router.get("/events/{event_id}")
def get_event(event_id: int, db: Session = Depends(get_db)):
    """One event and every connector call it caused."""
    event = db.query(GrowthEvent).filter(GrowthEvent.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    actions = (
        db.query(GrowthAction)
        .filter(GrowthAction.event_id == event_id)
        .order_by(GrowthAction.id)
        .all()
    )
    return event_to_dict(event, actions)
