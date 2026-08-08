"""Telegram Bot API connector.

Contract verified 2026-08-08 against https://core.telegram.org/bots/api and
https://core.telegram.org/bots/faq — see `docs/research/GROWTH_AI_INTEGRATION_RESEARCH.md` §5.

Today this is the outbound leg of the Growth AI flow, and it delivers to the
salon operator rather than to a client (ADR-002 decision 5). Nothing here sets
a webhook: `setWebhook` irreversibly disables `getUpdates` for the bot, and
inbound Telegram is not on today's path.
"""

from __future__ import annotations

import re
from typing import Any

import requests

from app.integrations.gateway import capabilities
from app.integrations.gateway.base_connector import BaseConnector

API_ROOT = "https://api.telegram.org"

_TOKEN_IN_URL = re.compile(r"/bot[^/\s]+")


class TelegramError(Exception):
    pass


def _redact(text: str) -> str:
    """Strip the bot token out of anything derived from a URL.

    `requests` puts the full URL into its exception messages, and the token
    sits in the path. Without this the token reaches the log the first time
    the network hiccups.
    """
    return _TOKEN_IN_URL.sub("/bot<redacted>", text)


class TelegramConnector(BaseConnector):
    integration_name = "telegram"

    SEND_MESSAGE_CAPABILITY = "telegram.send_message"

    # "In a single chat, avoid sending more than one message per second."
    min_interval_seconds = 1.0

    def __init__(
        self,
        *,
        bot_token: str = "",
        default_chat_id: str = "",
        timeout: int = 10,
        session: requests.Session | None = None,
    ) -> None:
        self.bot_token = bot_token.strip()
        self.default_chat_id = str(default_chat_id or "").strip()
        self.timeout = timeout
        self._session = session or requests.Session()

    @property
    def capabilities(self) -> set[str]:
        return {capabilities.MESSAGE_SEND, self.SEND_MESSAGE_CAPABILITY}

    def is_configured(self) -> bool:
        return bool(self.bot_token) and bool(self.default_chat_id)

    def missing_configuration(self) -> tuple[str, ...]:
        missing = []
        if not self.bot_token:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not self.default_chat_id:
            missing.append("TELEGRAM_OPERATOR_CHAT_ID")
        return tuple(missing)

    def rate_limit_key(self, capability: str, payload: dict[str, Any] | None) -> str:
        """Telegram's limit is per chat, so the bucket must be too."""
        chat_id = (payload or {}).get("chat_id") or self.default_chat_id or "-"
        return f"telegram:{chat_id}"

    def execute(self, capability: str, *, payload: dict[str, Any] | None = None) -> Any:
        if capability not in self.capabilities:
            raise ValueError(f"Unsupported capability for Telegram connector: {capability}")
        return self._send_message(payload or {})

    def _send_message(self, payload: dict[str, Any]) -> dict[str, Any]:
        chat_id = payload.get("chat_id") or self.default_chat_id
        if not chat_id:
            raise TelegramError("sendMessage needs a chat_id and no default is configured")

        text = payload.get("text")
        if not text:
            raise TelegramError("sendMessage needs a non-empty text")

        body: dict[str, Any] = {"chat_id": chat_id, "text": text}

        # parse_mode stays unset unless asked for. A client message containing
        # '_' or '*' makes a Markdown-parsed send fail — and that failure would
        # land on the operator alert, exactly when nobody is watching.
        if payload.get("parse_mode"):
            body["parse_mode"] = payload["parse_mode"]
        if payload.get("disable_notification") is not None:
            body["disable_notification"] = bool(payload["disable_notification"])
        if payload.get("reply_markup") is not None:
            body["reply_markup"] = payload["reply_markup"]

        url = f"{API_ROOT}/bot{self.bot_token}/sendMessage"

        try:
            response = self._session.post(url, json=body, timeout=self.timeout)
        except requests.RequestException as exc:
            raise TelegramError(f"sendMessage request failed: {_redact(str(exc))}") from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise TelegramError(
                f"sendMessage returned non-JSON (HTTP {response.status_code})"
            ) from exc

        # An HTTP 200 carrying ok:false is a failure. Checking the status code
        # alone is the most common way a Telegram integration silently stops
        # working.
        if not data.get("ok"):
            raise TelegramError(
                f"Telegram rejected sendMessage: "
                f"error_code={data.get('error_code')} "
                f"description={data.get('description')!r}"
            )

        return data.get("result", {})
