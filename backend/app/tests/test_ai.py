import uuid
from unittest.mock import AsyncMock, patch

from app.core.config import settings
from app.models.conversation import Message
from app.tests.testdb import TestingSessionLocal, client


def _create_conversation_with_messages() -> int:
    unique_phone = f"+1{uuid.uuid4().int % 10**9:09d}"
    client.post(
        "/clients",
        json={"first_name": "AI", "last_name": "Tester", "phone": unique_phone},
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
            "content": "Hello, I want to book an appointment",
        },
    )
    client.post(
        f"/conversations/{conversation_id}/messages",
        json={
            "channel": "whatsapp",
            "direction": "outbound",
            "content": "Sure, what service are you interested in?",
        },
    )

    return conversation_id


def test_ai_reply_not_configured(setup_test_db, monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    conversation_id = _create_conversation_with_messages()

    response = client.post("/ai/reply", json={"conversation_id": conversation_id})

    assert response.status_code == 503
    assert response.json()["detail"] == "LLM is not configured"


def test_ai_reply_conversation_not_found(setup_test_db, monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test-key")

    response = client.post("/ai/reply", json={"conversation_id": 999999})

    assert response.status_code == 404


def test_ai_reply_success(setup_test_db, monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test-key")
    conversation_id = _create_conversation_with_messages()

    with patch("app.api.ai.LLMService") as mock_llm_service_cls:
        mock_instance = mock_llm_service_cls.return_value
        mock_instance.reply = AsyncMock(return_value="We offer haircuts and coloring.")

        response = client.post("/ai/reply", json={"conversation_id": conversation_id})

    assert response.status_code == 200
    assert response.json() == {"reply": "We offer haircuts and coloring."}

    called_messages = mock_instance.reply.call_args[0][0]
    assert called_messages == [
        {"role": "user", "content": "Hello, I want to book an appointment"},
        {"role": "assistant", "content": "Sure, what service are you interested in?"},
    ]


def test_ai_reply_does_not_persist_message(setup_test_db, monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test-key")
    conversation_id = _create_conversation_with_messages()

    db = TestingSessionLocal()
    try:
        count_before = (
            db.query(Message).filter(Message.conversation_id == conversation_id).count()
        )
    finally:
        db.close()

    with patch("app.api.ai.LLMService") as mock_llm_service_cls:
        mock_instance = mock_llm_service_cls.return_value
        mock_instance.reply = AsyncMock(return_value="Test reply")
        client.post("/ai/reply", json={"conversation_id": conversation_id})

    db = TestingSessionLocal()
    try:
        count_after = (
            db.query(Message).filter(Message.conversation_id == conversation_id).count()
        )
    finally:
        db.close()

    assert count_after == count_before
