import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.config import settings
from app.integrations.gateway import reset_connector_gateway_for_tests
from app.services.llm_service import INTENTS, LLMService
from app.tests.testdb import client


def _create_conversation_with_messages() -> int:
    unique_phone = f"+3{uuid.uuid4().int % 10**9:09d}"
    client.post(
        "/clients",
        json={"first_name": "Intent", "last_name": "Tester", "phone": unique_phone},
    )
    clients = client.get("/clients").json()
    client_id = clients[-1]["id"]

    conversation = client.post(
        "/conversations",
        json={
            "customer_id": client_id,
            "primary_channel": "whatsapp",
            "current_channel": "whatsapp",
            "status": "active",
        },
    ).json()
    conversation_id = conversation["id"]

    client.post(
        f"/conversations/{conversation_id}/messages",
        json={
            "channel": "whatsapp",
            "direction": "inbound",
            "content": "I want to book a haircut for Friday",
        },
    )
    client.post(
        f"/conversations/{conversation_id}/messages",
        json={
            "channel": "whatsapp",
            "direction": "outbound",
            "content": "Sure, what time works for you?",
        },
    )

    return conversation_id


def _mock_openai_response(payload: str) -> MagicMock:
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = payload
    return response


def test_analyze_not_configured(setup_test_db, monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    conversation_id = _create_conversation_with_messages()

    response = client.post("/ai/analyze", json={"conversation_id": conversation_id})

    assert response.status_code == 503
    assert response.json()["detail"] == "LLM is not configured"


def test_analyze_conversation_not_found(setup_test_db, monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test-key")

    response = client.post("/ai/analyze", json={"conversation_id": 999999})

    assert response.status_code == 404


def test_analyze_returns_intent_and_confidence(setup_test_db, monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test-key")
    conversation_id = _create_conversation_with_messages()

    with patch("app.api.ai.LLMService") as mock_llm_service_cls:
        mock_instance = mock_llm_service_cls.return_value
        mock_instance.classify = AsyncMock(
            return_value={"intent": "BOOKING", "confidence": 0.94}
        )

        response = client.post("/ai/analyze", json={"conversation_id": conversation_id})

    assert response.status_code == 200
    assert response.json() == {"intent": "BOOKING", "confidence": 0.94}

    mock_instance.classify.assert_awaited_once()
    called_messages = mock_instance.classify.call_args[0][0]
    assert called_messages == [
        {"role": "user", "content": "I want to book a haircut for Friday"},
        {"role": "assistant", "content": "Sure, what time works for you?"},
    ]


@pytest.mark.parametrize("intent", INTENTS)
def test_analyze_accepts_every_allowed_intent(setup_test_db, monkeypatch, intent):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test-key")
    conversation_id = _create_conversation_with_messages()

    with patch("app.api.ai.LLMService") as mock_llm_service_cls:
        mock_instance = mock_llm_service_cls.return_value
        mock_instance.classify = AsyncMock(
            return_value={"intent": intent, "confidence": 0.5}
        )

        response = client.post("/ai/analyze", json={"conversation_id": conversation_id})

    assert response.status_code == 200
    assert response.json()["intent"] == intent


@pytest.mark.asyncio
async def test_classify_parses_llm_json(monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test-key")
    reset_connector_gateway_for_tests()
    service = LLMService()
    service.gateway.execute_async = AsyncMock(
        return_value=_mock_openai_response(json.dumps({"intent": "PRICE", "confidence": 0.81}))
    )

    result = await service.classify([{"role": "user", "content": "How much is it?"}])

    assert result == {"intent": "PRICE", "confidence": 0.81}


@pytest.mark.asyncio
async def test_classify_falls_back_to_other_on_unknown_intent(monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test-key")
    reset_connector_gateway_for_tests()
    service = LLMService()
    service.gateway.execute_async = AsyncMock(
        return_value=_mock_openai_response(json.dumps({"intent": "BUY_SHAMPOO", "confidence": 0.7}))
    )

    result = await service.classify([{"role": "user", "content": "..."}])

    assert result["intent"] == "OTHER"


@pytest.mark.asyncio
async def test_classify_handles_missing_confidence(monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test-key")
    reset_connector_gateway_for_tests()
    service = LLMService()
    service.gateway.execute_async = AsyncMock(return_value=_mock_openai_response(json.dumps({"intent": "CANCEL"})))

    result = await service.classify([{"role": "user", "content": "..."}])

    assert result == {"intent": "CANCEL", "confidence": 0.0}
