"""Growth AI Telegram bot — the Product Owner's interface to Coloré OS.

Runs on the **host**, not in the backend container, because every question it
answers needs something the container cannot see: the git tree, `.colore/`,
`scripts/doctor.sh`, and the other containers.

Long polling rather than a webhook, deliberately. `setWebhook` irreversibly
disables `getUpdates` for the bot, and the bot has no public HTTPS endpoint of
its own. Polling also means no inbound port and no third component to keep
published.

Sending reuses the existing `TelegramConnector` — same rate limit, same
`ok:false` handling, same token redaction. Nothing about outbound messaging is
reimplemented here.

    python -m app.growth.bot          # from /root/colore-os/backend
"""

from __future__ import annotations

import logging
import os
import signal
import sys
import time

import requests

from app.core.config import settings
from app.growth import commands
from app.integrations.connectors.telegram_connector import (
    API_ROOT,
    TelegramConnector,
    TelegramError,
    _redact,
)

logger = logging.getLogger("colore.bot")

POLL_TIMEOUT = 25
"""Long-poll seconds. Telegram holds the request open until an update arrives."""

ERROR_BACKOFF = 5


class GrowthBot:
    def __init__(
        self,
        *,
        bot_token: str,
        owner_id: str,
        connector: TelegramConnector | None = None,
        session: requests.Session | None = None,
    ) -> None:
        self.bot_token = bot_token
        self.owner_id = str(owner_id).strip()
        self._session = session or requests.Session()
        self._connector = connector or TelegramConnector(
            bot_token=bot_token,
            default_chat_id=self.owner_id,
            session=self._session,
        )
        self._offset: int | None = None
        self._running = True

    # ------------------------------------------------------------- lifecycle

    def stop(self, *_: object) -> None:
        logger.info("stopping after the current poll")
        self._running = False

    def run(self) -> int:
        me = self._get_me()
        logger.info("bot @%s ready, answering owner %s only", me, self.owner_id)

        while self._running:
            try:
                updates = self._get_updates()
            except Exception as exc:  # noqa: BLE001
                logger.warning("getUpdates failed: %s", _redact(str(exc)))
                time.sleep(ERROR_BACKOFF)
                continue

            for update in updates:
                try:
                    self._handle_update(update)
                except Exception:  # noqa: BLE001
                    # One bad message must not end the session.
                    logger.exception("failed to handle update %s", update.get("update_id"))

        return 0

    # --------------------------------------------------------------- telegram

    def _get_me(self) -> str:
        response = self._session.get(
            f"{API_ROOT}/bot{self.bot_token}/getMe", timeout=15
        ).json()
        if not response.get("ok"):
            raise RuntimeError(f"getMe rejected: {response.get('description')}")
        return (response.get("result") or {}).get("username", "unknown")

    def _get_updates(self) -> list[dict]:
        params: dict[str, object] = {
            "timeout": POLL_TIMEOUT,
            "allowed_updates": '["message"]',
        }
        if self._offset is not None:
            params["offset"] = self._offset

        response = self._session.get(
            f"{API_ROOT}/bot{self.bot_token}/getUpdates",
            params=params,
            timeout=POLL_TIMEOUT + 10,
        ).json()

        if not response.get("ok"):
            # 409 here means a webhook is set on this bot; the two are exclusive.
            raise RuntimeError(f"getUpdates rejected: {response.get('description')}")

        updates = response.get("result") or []
        if updates:
            self._offset = max(u["update_id"] for u in updates) + 1
        return updates

    # ---------------------------------------------------------------- routing

    def _handle_update(self, update: dict) -> None:
        message = update.get("message") or {}
        chat_id = str((message.get("chat") or {}).get("id") or "")
        sender_id = str((message.get("from") or {}).get("id") or "")
        text = message.get("text") or ""

        if not text:
            return

        # Owner only. Anyone else is logged and ignored — no reply, so the bot
        # does not confirm to a stranger that it is listening.
        if sender_id != self.owner_id:
            logger.warning("ignored message from %s", sender_id or "unknown")
            return

        command = commands.route(text)
        logger.info("owner asked %r -> %s", text[:60], command or "unknown")

        if command is None:
            self._reply(chat_id, commands.unknown_answer(text))
            return

        answer = commands.handle(command)
        self._reply(chat_id, answer)

    def _reply(self, chat_id: str, text: str) -> None:
        try:
            self._connector.execute("message.send", payload={"chat_id": chat_id, "text": text})
        except TelegramError as exc:
            logger.error("reply failed: %s", exc)


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    token = settings.TELEGRAM_BOT_TOKEN
    owner = settings.TELEGRAM_OWNER_ID or settings.TELEGRAM_OPERATOR_CHAT_ID

    missing = []
    if not token:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not owner:
        missing.append("TELEGRAM_OWNER_ID")
    if missing:
        logger.error("cannot start: missing %s", ", ".join(missing))
        return 1

    bot = GrowthBot(bot_token=token, owner_id=owner)
    signal.signal(signal.SIGTERM, bot.stop)
    signal.signal(signal.SIGINT, bot.stop)

    logger.info("repository: %s", os.getenv("COLORE_REPO_ROOT", "(derived from module path)"))
    return bot.run()


if __name__ == "__main__":
    sys.exit(main())
