import uuid
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.booking import PROPOSAL_SLOTS
from app.core.config import settings
from app.db.base import Base
from app.db.database import get_db
from app.main import app
from app.models.conversation import Message
from app.services.llm_service import INTENTS

engine_test = create_engine(settings.DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="session")
def setup_test_db():
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


def _create_conversation_with_messages() -> int:
    unique_phone = f"+5{uuid.uuid4().int % 10**9:09d}"
    client.post(
        "/clients",
        json={"first_name": "Flow", "last_name": "Tester", "phone": unique_phone},
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
            "content": "Can I come in for colouring this week?",
        },
    )
    client.post(
        f"/conversations/{conversation_id}/messages",
        json={
            "channel": "whatsapp",
            "direction": "outbound",
            "content": "Of course, let me check the schedule.",
        },
    )

    return conversation_id


def _mock_llm(reply: str, intent: str, confidence: float):
    """Patch LLMService used by the process endpoint and return the instance."""
    patcher = patch("app.api.conversations.LLMService")
    mock_cls = patcher.start()
    instance = mock_cls.return_value
    instance.reply = AsyncMock(return_value=reply)
    instance.classify = AsyncMock(
        return_value={"intent": intent, "confidence": confidence}
    )
    return patcher, instance


def _count_messages(conversation_id: int) -> int:
    db = TestingSessionLocal()
    try:
        return (
            db.query(Message).filter(Message.conversation_id == conversation_id).count()
        )
    finally:
        db.close()


def test_process_not_configured(setup_test_db, monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    conversation_id = _create_conversation_with_messages()

    response = client.post(f"/conversations/{conversation_id}/process")

    assert response.status_code == 503
    assert response.json()["detail"] == "LLM is not configured"


def test_process_conversation_not_found(setup_test_db, monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test-key")

    response = client.post("/conversations/999999/process")

    assert response.status_code == 404


def test_process_returns_slots_when_booking(setup_test_db, monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test-key")
    conversation_id = _create_conversation_with_messages()

    patcher, _ = _mock_llm("We have openings this week.", "BOOKING", 0.95)
    try:
        response = client.post(f"/conversations/{conversation_id}/process")
    finally:
        patcher.stop()

    assert response.status_code == 200
    assert response.json() == {
        "reply": "We have openings this week.",
        "intent": "BOOKING",
        "confidence": 0.95,
        "slots": PROPOSAL_SLOTS,
    }


@pytest.mark.parametrize(
    "intent", [intent for intent in INTENTS if intent != "BOOKING"]
)
def test_process_returns_empty_slots_when_not_booking(
    setup_test_db, monkeypatch, intent
):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test-key")
    conversation_id = _create_conversation_with_messages()

    patcher, _ = _mock_llm("Here is some information.", intent, 0.72)
    try:
        response = client.post(f"/conversations/{conversation_id}/process")
    finally:
        patcher.stop()

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == intent
    assert body["confidence"] == 0.72
    assert body["reply"] == "Here is some information."
    assert body["slots"] == []


def test_process_calls_reply_and_classify_with_same_history(setup_test_db, monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test-key")
    conversation_id = _create_conversation_with_messages()

    patcher, instance = _mock_llm("Sure.", "BOOKING", 0.9)
    try:
        client.post(f"/conversations/{conversation_id}/process")
    finally:
        patcher.stop()

    expected_history = [
        {"role": "user", "content": "Can I come in for colouring this week?"},
        {"role": "assistant", "content": "Of course, let me check the schedule."},
    ]

    instance.reply.assert_awaited_once()
    instance.classify.assert_awaited_once()
    assert instance.reply.call_args[0][0] == expected_history
    assert instance.classify.call_args[0][0] == expected_history


def test_process_does_not_persist_message(setup_test_db, monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test-key")
    conversation_id = _create_conversation_with_messages()

    count_before = _count_messages(conversation_id)

    patcher, _ = _mock_llm("Nothing is stored.", "OTHER", 0.4)
    try:
        response = client.post(f"/conversations/{conversation_id}/process")
    finally:
        patcher.stop()

    assert response.status_code == 200
    assert _count_messages(conversation_id) == count_before
