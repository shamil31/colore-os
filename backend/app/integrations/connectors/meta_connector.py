"""Meta webhook connector — verification and payload authenticity only.

Contract verified 2026-08-08 against
https://developers.facebook.com/docs/graph-api/webhooks/getting-started —
see `docs/research/GROWTH_AI_INTEGRATION_RESEARCH.md` §1.

Deliberately minimal. n8n owns the Meta subscription today (ADR-002 decision 4),
so this connector does not send anything and does not hold the subscription. It
exists because the two mechanisms that gate a direct Meta → Coloré OS webhook —
the `hub.challenge` handshake and `X-Hub-Signature-256` — cannot be added later
without redesign, and neither can be tested at all until they exist.
"""

from __future__ import annotations

import hashlib
import hmac
from typing import Any

from app.integrations.gateway import capabilities

from app.integrations.gateway.base_connector import BaseConnector

SIGNATURE_HEADER = "X-Hub-Signature-256"
SIGNATURE_PREFIX = "sha256="


class MetaVerificationError(Exception):
    pass


class MetaConnector(BaseConnector):
    integration_name = "meta"

    VERIFY_SIGNATURE_CAPABILITY = "meta.verify_signature"

    def __init__(
        self,
        *,
        app_secret: str = "",
        verify_token: str = "",
        api_version: str = "v23.0",
    ) -> None:
        self.app_secret = app_secret.strip()
        self.verify_token = verify_token.strip()
        # Pinned in one place. An unversioned Graph call silently gets the
        # oldest available version.
        self.api_version = api_version.strip() or "v23.0"

    @property
    def capabilities(self) -> set[str]:
        return {capabilities.EVENT_VERIFY, self.VERIFY_SIGNATURE_CAPABILITY}

    def is_configured(self) -> bool:
        return bool(self.verify_token)

    def missing_configuration(self) -> tuple[str, ...]:
        return () if self.verify_token else ("META_VERIFY_TOKEN",)

    @property
    def can_verify_signatures(self) -> bool:
        return bool(self.app_secret)

    def execute(self, capability: str, *, payload: dict[str, Any] | None = None) -> Any:
        body = payload or {}

        if capability == capabilities.EVENT_VERIFY:
            return self.verify_subscription(
                mode=body.get("hub.mode"),
                token=body.get("hub.verify_token"),
                challenge=body.get("hub.challenge"),
            )

        if capability == self.VERIFY_SIGNATURE_CAPABILITY:
            return self.verify_signature(
                raw_body=body.get("raw_body"),
                signature_header=body.get("signature_header"),
            )

        raise ValueError(f"Unsupported capability for Meta connector: {capability}")

    def verify_subscription(
        self,
        *,
        mode: str | None,
        token: str | None,
        challenge: str | None,
    ) -> str:
        """Answer the GET handshake. Returns the challenge to echo verbatim."""
        if not self.verify_token:
            raise MetaVerificationError("META_VERIFY_TOKEN is not configured")

        if mode != "subscribe":
            raise MetaVerificationError(f"unexpected hub.mode: {mode!r}")

        if not token or not hmac.compare_digest(token, self.verify_token):
            raise MetaVerificationError("hub.verify_token does not match")

        if challenge is None:
            raise MetaVerificationError("hub.challenge is missing")

        return str(challenge)

    def verify_signature(self, *, raw_body: Any, signature_header: str | None) -> bool:
        """Check X-Hub-Signature-256 over the **raw** request body.

        Meta signs the bytes it sent. Any code that re-serialises the parsed
        JSON before signing will produce a mismatch on payloads that are
        semantically identical, so this refuses anything but bytes.
        """
        if not self.app_secret:
            raise MetaVerificationError("META_APP_SECRET is not configured")

        if not isinstance(raw_body, (bytes, bytearray)):
            raise MetaVerificationError(
                "signature must be checked against the raw request body as bytes"
            )

        if not signature_header:
            raise MetaVerificationError(f"{SIGNATURE_HEADER} is missing")

        if not signature_header.startswith(SIGNATURE_PREFIX):
            raise MetaVerificationError(
                f"{SIGNATURE_HEADER} must start with {SIGNATURE_PREFIX!r}"
            )

        provided = signature_header[len(SIGNATURE_PREFIX) :]
        expected = hmac.new(
            self.app_secret.encode("utf-8"),
            bytes(raw_body),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(provided, expected):
            raise MetaVerificationError("signature does not match the request body")

        return True
