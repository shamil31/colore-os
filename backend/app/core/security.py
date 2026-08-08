"""API access control.

Deny by default. Every route is protected unless it is named here, so a new
endpoint is safe the day it is written rather than the day somebody remembers
to add a dependency to it. That ordering matters: the breach this module exists
to close was not a route with the wrong decorator, it was five routes that
never had one.

Two secrets, two trust boundaries, deliberately not shared:

- `X-Colore-Api-Key` (`COLORE_API_TOKEN`) — reading business data. Used by the
  Growth AI bot, the doctor, and the owner.
- `X-Colore-Token` (`GROWTH_INBOUND_SECRET`) — the n8n ingest hop only,
  enforced by the endpoint itself.

Network position is never trusted. nginx proxies public traffic to
127.0.0.1:8000, so the application sees the same source address for a request
from the internet and one from this host. An IP allowlist here would be
security theatre.
"""

from __future__ import annotations

import hmac
import logging

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("colore.security")

API_KEY_HEADER = "X-Colore-Api-Key"

# Paths anyone may call. Nothing here returns client data.
PUBLIC_PATHS: frozenset[tuple[str, str]] = frozenset(
    {
        ("GET", "/"),            # version and liveness
        ("GET", "/docs"),
        ("GET", "/redoc"),
        ("GET", "/openapi.json"),
        ("GET", "/docs/oauth2-redirect"),
    }
)

PUBLIC_PREFIXES: tuple[str, ...] = (
    "/ui",  # static page; every call it makes is itself authenticated
)

# Routes that authenticate themselves, with a different secret or mechanism.
# The middleware steps aside; the endpoint is responsible.
SELF_AUTHENTICATED: frozenset[tuple[str, str]] = frozenset(
    {
        # n8n ingest — shared secret, checked by require_inbound_token
        ("POST", "/growth/events"),
        # Meta must be able to reach these. Verified by hub.verify_token and
        # X-Hub-Signature-256 respectively; a key would make them unusable.
        ("GET", "/growth/webhook/meta"),
        ("POST", "/growth/webhook/meta"),
    }
)


def _normalise(path: str) -> str:
    if len(path) > 1 and path.endswith("/"):
        return path[:-1]
    return path


def is_public(method: str, path: str) -> bool:
    path = _normalise(path)
    if (method, path) in PUBLIC_PATHS:
        return True
    return any(path == prefix or path.startswith(prefix + "/") for prefix in PUBLIC_PREFIXES)


def is_self_authenticated(method: str, path: str) -> bool:
    return (method, _normalise(path)) in SELF_AUTHENTICATED


def _unauthorised(detail: str, status_code: int = 401) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": detail})


async def api_key_middleware(request: Request, call_next):
    method = request.method.upper()
    path = request.url.path

    if method == "OPTIONS" or is_public(method, path) or is_self_authenticated(method, path):
        return await call_next(request)

    from app.core.config import settings

    expected = (settings.COLORE_API_TOKEN or "").strip()
    if not expected:
        # Fail closed. An unset key must never mean "open to everyone" — that
        # is precisely how business data ended up on the public internet.
        logger.error("COLORE_API_TOKEN is not configured; refusing %s %s", method, path)
        return _unauthorised(
            "COLORE_API_TOKEN is not configured — this endpoint is disabled "
            "rather than left open",
            status_code=503,
        )

    provided = request.headers.get(API_KEY_HEADER, "")
    if not provided or not hmac.compare_digest(provided, expected):
        logger.warning("rejected %s %s: missing or invalid %s", method, path, API_KEY_HEADER)
        return _unauthorised(f"missing or invalid {API_KEY_HEADER}")

    return await call_next(request)
