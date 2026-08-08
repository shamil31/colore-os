"""The end-to-end Growth AI flow.

    Meta → n8n → Coloré OS → Growth AI → Telegram

These run the real pipeline: the HTTP endpoint, normalisation, deduplication,
the decision, the gateway dispatch and the trace. Only the Telegram network
call is faked.
"""

import pytest

from app.core.config import settings
from app.integrations.connectors.telegram_connector import TelegramConnector
from app.integrations.gateway import reset_connector_gateway_for_tests
from app.integrations.gateway.factory import get_connector_gateway
from app.tests.test_growth_normalize import instagram_payload, whatsapp_payload
from app.tests.testdb import client

SECRET = "test-inbound-secret"
HEADERS = {"X-Colore-Token": SECRET}


class RecordingSession:
    def __init__(self):
        self.calls = []

    def post(self, url, json=None, headers=None, timeout=None):
        self.calls.append({"url": url, "json": json})
        return _Ok()


class _Ok:
    status_code = 200

    def json(self):
        return {"ok": True, "result": {"message_id": 1}}


@pytest.fixture
def inbound_secret(monkeypatch):
    monkeypatch.setattr(settings, "GROWTH_INBOUND_SECRET", SECRET)
    # No key means no classifier, so these tests never reach the network.
    # Intent then routes to UNKNOWN, which is the production behaviour when
    # OpenAI is unavailable. The classified path is covered separately below.
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    reset_connector_gateway_for_tests()
    yield
    reset_connector_gateway_for_tests()


@pytest.fixture
def telegram(monkeypatch, inbound_secret):
    """Register a configured Telegram connector with a fake network."""
    session = RecordingSession()
    gateway = get_connector_gateway()
    gateway.integration_registry._connectors["telegram"] = TelegramConnector(
        bot_token="TEST", default_chat_id="777", session=session
    )
    gateway.rate_limiter.reset()
    return session


# ------------------------------------------------------------------- ingress


def test_inbound_endpoint_rejects_a_request_without_the_token(inbound_secret):
    response = client.post("/growth/events", json=whatsapp_payload())

    assert response.status_code == 401


def test_inbound_endpoint_rejects_a_wrong_token(inbound_secret):
    response = client.post(
        "/growth/events",
        json=whatsapp_payload(),
        headers={"X-Colore-Token": "guessed"},
    )

    assert response.status_code == 401


def test_inbound_endpoint_is_disabled_when_no_secret_is_configured(monkeypatch):
    monkeypatch.setattr(settings, "GROWTH_INBOUND_SECRET", "")

    response = client.post("/growth/events", json=whatsapp_payload(), headers=HEADERS)

    assert response.status_code == 503, "an unset secret must close the endpoint, not open it"


# -------------------------------------------------------------- full journey


def test_whatsapp_message_reaches_telegram(setup_test_db, telegram):
    response = client.post(
        "/growth/events",
        json=whatsapp_payload(text="Хочу записаться на завтра", message_id="wamid.E2E1"),
        headers=HEADERS,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["result"] == "processed"
    assert body["source"] == "whatsapp"
    assert body["dispatch"]["connector"] == "telegram"
    assert body["dispatch"]["status"] == "ok"

    sent = telegram.calls[0]["json"]
    assert sent["chat_id"] == "777"
    assert "Хочу записаться на завтра" in sent["text"]
    assert "WHATSAPP" in sent["text"]
    # parse_mode stays off so client punctuation cannot break the alert
    assert "parse_mode" not in sent


def test_instagram_message_reaches_telegram(setup_test_db, telegram):
    response = client.post(
        "/growth/events",
        json=instagram_payload(text="Есть окно сегодня?", mid="mid.E2E2"),
        headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json()["source"] == "instagram"
    assert "Есть окно сегодня?" in telegram.calls[0]["json"]["text"]


def test_flow_records_a_queryable_trace(setup_test_db, telegram):
    created = client.post(
        "/growth/events",
        json=whatsapp_payload(text="Сколько стоит стрижка?", message_id="wamid.E2E3"),
        headers=HEADERS,
    ).json()

    detail = client.get(f"/growth/events/{created['event_id']}")

    assert detail.status_code == 200
    event = detail.json()
    assert event["text"] == "Сколько стоит стрижка?"
    assert event["status"] == "processed"
    assert event["priority"] in ("high", "normal")
    assert event["decision_reason"], "every decision must say why, in words"

    action = event["actions"][0]
    assert action["connector"] == "telegram"
    assert action["capability"] == "message.send"
    assert action["status"] == "ok"


# ----------------------------------------------------------------- dedup


def test_a_retried_delivery_is_not_processed_twice(setup_test_db, telegram):
    """Meta retries for 36 hours and says deduplication is our job."""
    payload = whatsapp_payload(text="Дубликат", message_id="wamid.RETRY")

    first = client.post("/growth/events", json=payload, headers=HEADERS).json()
    second = client.post("/growth/events", json=payload, headers=HEADERS).json()

    assert first["result"] == "processed"
    assert second["result"] == "duplicate"
    assert second["event_id"] == first["event_id"]
    assert len(telegram.calls) == 1, "the operator must be alerted once, not twice"


def test_an_echo_is_skipped_and_never_alerts(setup_test_db, telegram):
    """The loop guard: answering our own message would talk to ourselves."""
    response = client.post(
        "/growth/events",
        json=instagram_payload(mid="mid.ECHO", is_echo=True),
        headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json()["reason"] == "echo"
    assert telegram.calls == []


# ---------------------------------------------------------------- dry run


def test_without_a_telegram_token_the_flow_completes_as_a_dry_run(setup_test_db, inbound_secret):
    """No credentials anywhere must still produce a complete, honest trace."""
    response = client.post(
        "/growth/events",
        json=whatsapp_payload(text="Без токена", message_id="wamid.DRY"),
        headers=HEADERS,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["result"] == "processed"
    assert body["dispatch"]["status"] == "dry_run"

    event = client.get(f"/growth/events/{body['event_id']}").json()
    assert event["actions"][0]["status"] == "dry_run"


# ------------------------------------------------------------ meta handshake


def test_meta_handshake_echoes_the_challenge(monkeypatch):
    monkeypatch.setattr(settings, "META_VERIFY_TOKEN", "verify-me")
    reset_connector_gateway_for_tests()

    response = client.get(
        "/growth/webhook/meta",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "verify-me",
            "hub.challenge": "1158201444",
        },
    )

    assert response.status_code == 200
    assert response.text == "1158201444"
    reset_connector_gateway_for_tests()


def test_meta_handshake_rejects_a_wrong_token(monkeypatch):
    monkeypatch.setattr(settings, "META_VERIFY_TOKEN", "verify-me")
    reset_connector_gateway_for_tests()

    response = client.get(
        "/growth/webhook/meta",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong",
            "hub.challenge": "1158201444",
        },
    )

    assert response.status_code == 403
    reset_connector_gateway_for_tests()


def test_direct_meta_webhook_is_closed_without_an_app_secret(monkeypatch):
    monkeypatch.setattr(settings, "META_APP_SECRET", "")
    reset_connector_gateway_for_tests()

    response = client.post("/growth/webhook/meta", json=whatsapp_payload())

    assert response.status_code == 503
    reset_connector_gateway_for_tests()


# ------------------------------------------------------------------ decision


@pytest.mark.asyncio
async def test_revenue_intent_is_high_priority():
    from app.growth.normalize import NormalisedEvent
    from app.services.growth_ai import GrowthAI

    class StubLLM:
        async def classify(self, messages):
            return {"intent": "BOOKING", "confidence": 0.92}

    decision = await GrowthAI(llm=StubLLM()).decide(
        NormalisedEvent(
            source="whatsapp",
            external_id="x",
            sender_ref="381641234567",
            text="Хочу записаться",
        )
    )

    assert decision.intent == "BOOKING"
    assert decision.priority == "high"
    assert "revenue intent" in decision.reason


@pytest.mark.asyncio
async def test_a_classifier_outage_still_alerts_the_operator():
    """A broken classifier must not swallow a client's message."""
    from app.growth.normalize import NormalisedEvent
    from app.services.growth_ai import GrowthAI

    class BrokenLLM:
        async def classify(self, messages):
            raise RuntimeError("openai is down")

    decision = await GrowthAI(llm=BrokenLLM()).decide(
        NormalisedEvent(source="instagram", external_id="x", sender_ref="IGSID", text="Привет")
    )

    assert decision.intent == "UNKNOWN"
    assert decision.priority == "normal"
    assert "Привет" in decision.alert_text


# ---------------------------------------------------------------- inspection


def test_integrations_endpoint_reports_configuration_state():
    response = client.get("/growth/integrations")

    assert response.status_code == 200
    names = {i["name"] for i in response.json()["integrations"]}
    assert {"telegram", "meta", "n8n", "altegio"} <= names
