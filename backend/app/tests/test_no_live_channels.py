"""The test suite must not be able to reach a real platform.

A regression here is not a failing assertion somewhere — it is a real message
arriving on the salon owner's phone during `pytest`. That happened once, on
2026-08-08, when Telegram credentials were added to `backend/.env` so the
host-side bot could run: a dry-run test started sending live messages.

The autouse guard lives in `conftest.py`. These tests keep it honest.
"""

from app.core.config import settings
from app.integrations.gateway.factory import get_connector_gateway
from app.tests.conftest import OUTBOUND_CREDENTIALS


def test_every_outbound_credential_is_blank_during_tests():
    for name in OUTBOUND_CREDENTIALS:
        assert getattr(settings, name) == "", f"{name} is set — tests could reach a real platform"


def test_no_channel_connector_reports_itself_configured():
    status = get_connector_gateway().status()

    live = [
        item["name"]
        for item in status["integrations"]
        if item["configured"] and item["name"] in {"telegram", "meta", "n8n", "altegio"}
    ]

    assert live == [], f"these connectors would make real calls in tests: {live}"


def test_message_send_has_no_configured_provider():
    status = get_connector_gateway().status()

    send = status["capabilities"].get("message.send", {})
    assert send.get("configured_providers") == [], (
        "message.send resolves to a live connector — a test could message a real person"
    )
