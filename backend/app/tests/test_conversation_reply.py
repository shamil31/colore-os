import uuid
from unittest.mock import AsyncMock, patch

from app.core.config import settings
from app.models.conversation import Message
from app.tests.testdb import TestingSessionLocal, client


def _create_conversation_with_messages(channel: str = "whatsapp") -> int:
    unique_phone = f"+2{uuid.uuid4().int % 10**9:09d}"
    client.post(
        "/clients",
        json={"first_name": "Loop", "last_name": "Tester", "phone": unique_phone},
    )
    clients = client.get("/clients").json()
    client_id = clients[-1]["id"]

    conversation = client.post(
        "/conversations",
        json={
            "customer_id": client_id,
            "primary_channel": channel,
            "current_channel": channel,
            "status": "active",
        },
    ).json()
    conversation_id = conversation["id"]

    client.post(
        f"/conversations/{conversation_id}/messages",
        json={
            "channel": channel,
            "direction": "inbound",
            "content": "Do you do balayage?",
        },
    )

    return conversation_id


def _count_messages(conversation_id: int) -> int:
    db = TestingSessionLocal()
    try:
        return (
            db.query(Message).filter(Message.conversation_id == conversation_id).count()
        )
    finally:
        db.close()


def test_reply_not_configured(setup_test_db, monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    conversation_id = _create_conversation_with_messages()

    response = client.post(f"/conversations/{conversation_id}/reply")

    assert response.status_code == 503
    assert response.json()["detail"] == "LLM is not configured"


def test_reply_conversation_not_found(setup_test_db, monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test-key")

    response = client.post("/conversations/999999/reply")

    assert response.status_code == 404


def test_reply_calls_llm_and_returns_reply(setup_test_db, monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test-key")
    conversation_id = _create_conversation_with_messages()

    with patch("app.api.conversations.LLMService") as mock_llm_service_cls:
        mock_instance = mock_llm_service_cls.return_value
        mock_instance.reply = AsyncMock(return_value="Yes, we do balayage.")

        response = client.post(f"/conversations/{conversation_id}/reply")

    assert response.status_code == 200
    body = response.json()
    assert body["reply"] == "Yes, we do balayage."
    assert isinstance(body["message_id"], int)

    mock_instance.reply.assert_awaited_once()
    called_messages = mock_instance.reply.call_args[0][0]
    assert called_messages == [
        {"role": "user", "content": "Do you do balayage?"},
    ]


def test_reply_creates_outbound_message(setup_test_db, monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test-key")
    conversation_id = _create_conversation_with_messages(channel="telegram")

    count_before = _count_messages(conversation_id)

    with patch("app.api.conversations.LLMService") as mock_llm_service_cls:
        mock_instance = mock_llm_service_cls.return_value
        mock_instance.reply = AsyncMock(return_value="Sure, let me check availability.")

        response = client.post(f"/conversations/{conversation_id}/reply")

    assert response.status_code == 200
    message_id = response.json()["message_id"]

    assert _count_messages(conversation_id) == count_before + 1

    db = TestingSessionLocal()
    try:
        message = db.query(Message).filter(Message.id == message_id).first()
    finally:
        db.close()

    assert message is not None
    assert message.conversation_id == conversation_id
    assert message.direction == "outbound"
    assert message.channel == "telegram"
    assert message.content == "Sure, let me check availability."
    assert message.created_at is not None


def test_reply_message_appears_in_history(setup_test_db, monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test-key")
    conversation_id = _create_conversation_with_messages()

    with patch("app.api.conversations.LLMService") as mock_llm_service_cls:
        mock_instance = mock_llm_service_cls.return_value
        mock_instance.reply = AsyncMock(return_value="First AI answer.")
        client.post(f"/conversations/{conversation_id}/reply")

    # A second reply must see the first AI answer in the history sent to the LLM.
    with patch("app.api.conversations.LLMService") as mock_llm_service_cls:
        mock_instance = mock_llm_service_cls.return_value
        mock_instance.reply = AsyncMock(return_value="Second AI answer.")
        client.post(f"/conversations/{conversation_id}/reply")

        called_messages = mock_instance.reply.call_args[0][0]

    assert called_messages == [
        {"role": "user", "content": "Do you do balayage?"},
        {"role": "assistant", "content": "First AI answer."},
    ]
