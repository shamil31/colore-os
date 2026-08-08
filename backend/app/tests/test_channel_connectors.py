"""Telegram, Meta and n8n connector contracts.

Each assertion below maps to a statement in the official documentation, quoted
in `docs/research/GROWTH_AI_INTEGRATION_RESEARCH.md`.
"""

import hashlib
import hmac

import pytest
import requests

from app.integrations.connectors.meta_connector import (
    MetaConnector,
    MetaVerificationError,
)
from app.integrations.connectors.n8n_connector import N8nConnector, N8nWorkflowError
from app.integrations.connectors.telegram_connector import (
    TelegramConnector,
    TelegramError,
)
from app.integrations.gateway import capabilities


class FakeResponse:
    def __init__(self, payload=None, status_code=200, text=""):
        self._payload = payload
        self.status_code = status_code
        self.text = text or ""

    def json(self):
        if self._payload is None:
            raise ValueError("not json")
        return self._payload


class FakeSession:
    """Records calls instead of making them."""

    def __init__(self, response=None, raises=None):
        self.response = response or FakeResponse({"ok": True, "result": {}})
        self.raises = raises
        self.calls = []

    def post(self, url, json=None, headers=None, timeout=None):
        self.calls.append({"url": url, "json": json, "headers": headers})
        if self.raises:
            raise self.raises
        return self.response


# ------------------------------------------------------------------ telegram


def test_telegram_sends_chat_id_and_text():
    session = FakeSession(FakeResponse({"ok": True, "result": {"message_id": 7}}))
    connector = TelegramConnector(bot_token="T", default_chat_id="42", session=session)

    result = connector.execute(capabilities.MESSAGE_SEND, payload={"text": "hello"})

    assert result == {"message_id": 7}
    assert session.calls[0]["json"] == {"chat_id": "42", "text": "hello"}


def test_telegram_treats_ok_false_as_failure_even_on_http_200():
    """An HTTP 200 carrying ok:false is a failure — the envelope is the truth."""
    session = FakeSession(
        FakeResponse(
            {"ok": False, "error_code": 400, "description": "chat not found"},
            status_code=200,
        )
    )
    connector = TelegramConnector(bot_token="T", default_chat_id="42", session=session)

    with pytest.raises(TelegramError) as exc:
        connector.execute(capabilities.MESSAGE_SEND, payload={"text": "hello"})

    assert "chat not found" in str(exc.value)
    assert "400" in str(exc.value)


def test_telegram_omits_parse_mode_unless_asked():
    """Markdown in a client's message must not be able to break an alert."""
    session = FakeSession()
    connector = TelegramConnector(bot_token="T", default_chat_id="42", session=session)

    connector.execute(capabilities.MESSAGE_SEND, payload={"text": "price is 50_000 *net*"})

    assert "parse_mode" not in session.calls[0]["json"]


def test_telegram_never_leaks_the_token_in_an_error():
    session = FakeSession(
        raises=requests.ConnectionError(
            "HTTPSConnectionPool(host='api.telegram.org', port=443): "
            "Max retries exceeded with url: /bot123456:SUPERSECRET/sendMessage"
        )
    )
    connector = TelegramConnector(bot_token="123456:SUPERSECRET", default_chat_id="42", session=session)

    with pytest.raises(TelegramError) as exc:
        connector.execute(capabilities.MESSAGE_SEND, payload={"text": "hi"})

    assert "SUPERSECRET" not in str(exc.value)
    assert "<redacted>" in str(exc.value)


def test_telegram_rate_limit_bucket_is_per_chat():
    connector = TelegramConnector(bot_token="T", default_chat_id="42")

    assert connector.min_interval_seconds == 1.0
    assert connector.rate_limit_key(capabilities.MESSAGE_SEND, {"chat_id": 9}) == "telegram:9"
    assert connector.rate_limit_key(capabilities.MESSAGE_SEND, {}) == "telegram:42"


def test_telegram_without_settings_is_unconfigured():
    connector = TelegramConnector()

    assert connector.is_configured() is False
    assert connector.missing_configuration() == (
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_OPERATOR_CHAT_ID",
    )


def test_telegram_rejects_empty_text():
    connector = TelegramConnector(bot_token="T", default_chat_id="42", session=FakeSession())

    with pytest.raises(TelegramError):
        connector.execute(capabilities.MESSAGE_SEND, payload={"text": ""})


# ---------------------------------------------------------------------- meta


def test_meta_echoes_the_challenge_when_the_token_matches():
    connector = MetaConnector(verify_token="secret-token")

    result = connector.execute(
        capabilities.EVENT_VERIFY,
        payload={
            "hub.mode": "subscribe",
            "hub.verify_token": "secret-token",
            "hub.challenge": "1158201444",
        },
    )

    assert result == "1158201444"


def test_meta_rejects_a_wrong_verify_token():
    connector = MetaConnector(verify_token="secret-token")

    with pytest.raises(MetaVerificationError):
        connector.execute(
            capabilities.EVENT_VERIFY,
            payload={
                "hub.mode": "subscribe",
                "hub.verify_token": "guessed",
                "hub.challenge": "123",
            },
        )


def test_meta_rejects_a_mode_that_is_not_subscribe():
    connector = MetaConnector(verify_token="t")

    with pytest.raises(MetaVerificationError):
        connector.verify_subscription(mode="unsubscribe", token="t", challenge="1")


def test_meta_accepts_a_correct_signature_over_the_raw_body():
    secret = "app-secret"
    raw = b'{"object":"instagram","entry":[]}'
    digest = hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()
    connector = MetaConnector(app_secret=secret, verify_token="t")

    assert connector.verify_signature(raw_body=raw, signature_header=f"sha256={digest}") is True


def test_meta_rejects_a_signature_computed_over_different_bytes():
    secret = "app-secret"
    raw = b'{"object":"instagram","entry":[]}'
    # Same JSON, re-serialised with spaces — semantically identical, different
    # bytes. Meta signs bytes, so this must fail.
    reserialised = b'{"object": "instagram", "entry": []}'
    digest = hmac.new(secret.encode(), reserialised, hashlib.sha256).hexdigest()
    connector = MetaConnector(app_secret=secret, verify_token="t")

    with pytest.raises(MetaVerificationError):
        connector.verify_signature(raw_body=raw, signature_header=f"sha256={digest}")


def test_meta_refuses_to_verify_a_parsed_body():
    connector = MetaConnector(app_secret="s", verify_token="t")

    with pytest.raises(MetaVerificationError) as exc:
        connector.verify_signature(raw_body={"object": "instagram"}, signature_header="sha256=x")

    assert "raw request body" in str(exc.value)


def test_meta_requires_the_sha256_prefix():
    connector = MetaConnector(app_secret="s", verify_token="t")

    with pytest.raises(MetaVerificationError):
        connector.verify_signature(raw_body=b"{}", signature_header="deadbeef")


def test_meta_without_a_verify_token_is_unconfigured():
    connector = MetaConnector()

    assert connector.is_configured() is False
    assert connector.missing_configuration() == ("META_VERIFY_TOKEN",)


# ----------------------------------------------------------------------- n8n


def test_n8n_posts_the_payload_with_the_auth_header():
    session = FakeSession(FakeResponse({"received": True}))
    connector = N8nConnector(
        workflow_url="https://n8n.colorebl.com/webhook/growth",
        auth_header="X-Colore-Token",
        auth_token="shared",
        session=session,
    )

    result = connector.execute(capabilities.WORKFLOW_TRIGGER, payload={"event_id": "e1"})

    assert result == {"received": True}
    assert session.calls[0]["url"] == "https://n8n.colorebl.com/webhook/growth"
    assert session.calls[0]["json"] == {"event_id": "e1"}
    assert session.calls[0]["headers"]["X-Colore-Token"] == "shared"


def test_n8n_404_says_the_workflow_is_probably_unpublished():
    session = FakeSession(FakeResponse(None, status_code=404, text="not registered"))
    connector = N8nConnector(workflow_url="https://n8n.colorebl.com/webhook/growth", session=session)

    with pytest.raises(N8nWorkflowError) as exc:
        connector.execute(capabilities.WORKFLOW_TRIGGER, payload={})

    assert "not published" in str(exc.value)


def test_n8n_tolerates_a_non_json_respond_immediately_answer():
    session = FakeSession(FakeResponse(None, status_code=200, text="Workflow got started"))
    connector = N8nConnector(workflow_url="https://n8n.colorebl.com/webhook/growth", session=session)

    result = connector.execute(capabilities.WORKFLOW_TRIGGER, payload={})

    assert result == {"status_code": 200, "body": "Workflow got started"}


def test_n8n_without_a_url_is_unconfigured():
    connector = N8nConnector()

    assert connector.is_configured() is False
    assert connector.missing_configuration() == ("N8N_WORKFLOW_URL",)
