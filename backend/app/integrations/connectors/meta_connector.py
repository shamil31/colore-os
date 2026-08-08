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

import requests

from app.integrations.gateway import capabilities

from app.integrations.gateway.base_connector import BaseConnector

SIGNATURE_HEADER = "X-Hub-Signature-256"
SIGNATURE_PREFIX = "sha256="

GRAPH_HOST = "https://graph.facebook.com"


class MetaVerificationError(Exception):
    pass


class MetaSendError(MetaVerificationError):
    """A Conversions API send that did not succeed, with enough detail to judge
    whether trying again could ever help.

    Subclasses `MetaVerificationError` so existing callers keep working.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        error_code: int | None = None,
        error_subcode: int | None = None,
        is_transient: bool | None = None,
        network: bool = False,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.error_subcode = error_subcode
        # Meta sets `is_transient` on its own errors when it knows the answer.
        self.is_transient = is_transient
        self.network = network


class MetaConnector(BaseConnector):
    integration_name = "meta"

    VERIFY_SIGNATURE_CAPABILITY = "meta.verify_signature"
    SEND_CONVERSIONS_CAPABILITY = "meta.send_conversions"

    def __init__(
        self,
        *,
        app_secret: str = "",
        verify_token: str = "",
        api_version: str = "v23.0",
        access_token: str = "",
        dataset_id: str = "",
        test_event_code: str = "",
        timeout: int = 20,
        session: requests.Session | None = None,
    ) -> None:
        self.test_event_code = test_event_code.strip()
        self.app_secret = app_secret.strip()
        self.verify_token = verify_token.strip()
        self.access_token = access_token.strip()
        self.dataset_id = dataset_id.strip()
        self.timeout = timeout
        self._session = session or requests.Session()
        # Pinned in one place. An unversioned Graph call silently gets the
        # oldest available version.
        self.api_version = api_version.strip() or "v23.0"

    @property
    def capabilities(self) -> set[str]:
        return {
            capabilities.EVENT_VERIFY,
            self.VERIFY_SIGNATURE_CAPABILITY,
            self.SEND_CONVERSIONS_CAPABILITY,
        }

    def is_configured(self) -> bool:
        return bool(self.verify_token)

    def missing_configuration(self) -> tuple[str, ...]:
        return () if self.verify_token else ("META_VERIFY_TOKEN",)

    @property
    def can_verify_signatures(self) -> bool:
        return bool(self.app_secret)

    @property
    def can_send_conversions(self) -> bool:
        return bool(self.access_token and self.dataset_id)

    def missing_conversion_settings(self) -> tuple[str, ...]:
        missing = []
        if not self.access_token:
            missing.append("META_ACCESS_TOKEN")
        if not self.dataset_id:
            missing.append("META_DATASET_ID")
        return tuple(missing)

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

        if capability == self.SEND_CONVERSIONS_CAPABILITY:
            return self.send_conversions(body.get("data") or [])

        raise ValueError(f"Unsupported capability for Meta connector: {capability}")

    def send_conversions(
        self,
        events: list[dict[str, Any]],
        *,
        test_event_code: str | None = None,
    ) -> dict[str, Any]:
        """POST /{dataset_id}/events — the Conversions API.

        Refuses rather than pretends when it cannot send. A silent no-op here
        would make the queue look drained while Meta received nothing.
        """
        if not self.can_send_conversions:
            raise MetaVerificationError(
                "not configured: " + ", ".join(self.missing_conversion_settings())
            )

        if not events:
            return {"events_received": 0}

        url = f"{GRAPH_HOST}/{self.api_version}/{self.dataset_id}/events"

        body: dict[str, Any] = {"data": events, "access_token": self.access_token}

        # With a test event code, events appear in Events Manager's Test Events
        # view and do not affect ad delivery. It is the only way to prove the
        # pipeline works without putting real traffic against a live account.
        code = test_event_code if test_event_code is not None else self.test_event_code
        if code:
            body["test_event_code"] = code

        try:
            response = self._session.post(
                url,
                json=body,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            # Never reached Meta. The events are untouched by definition.
            raise MetaSendError(f"conversions request failed: {exc}", network=True) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise MetaSendError(
                f"conversions returned non-JSON (HTTP {response.status_code})",
                status_code=response.status_code,
            ) from exc

        if response.status_code >= 400 or "error" in payload:
            error = payload.get("error") or {}
            raise MetaSendError(
                f"Meta rejected the events: HTTP {response.status_code} "
                f"{error.get('type', '')} {error.get('message', '')}".strip(),
                status_code=response.status_code,
                error_code=error.get("code"),
                error_subcode=error.get("error_subcode"),
                is_transient=error.get("is_transient"),
            )

        return payload

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
