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
    unique_phone = f"+4{uuid.uuid4().int % 10**9:09d}"
    client.post(
        "/clients",
        json={"first_name": "Booking", "last_name": "Tester", "phone": unique_phone},
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
            "content": "I would like to come in for a haircut",
        },
    )
    client.post(
        f"/conversations/{conversation_id}/messages",
        json={
            "channel": "whatsapp",
            "direction": "outbound",
            "content": "Of course, when suits you?",
        },
    )

    return conversation_id


def test_proposal_not_configured(setup_test_db, monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    conversation_id = _create_conversation_with_messages()

    response = client.post(
        "/booking/proposal", json={"conversation_id": conversation_id}
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "LLM is not configured"


def test_proposal_conversation_not_found(setup_test_db, monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test-key")

    response = client.post("/booking/proposal", json={"conversation_id": 999999})

    assert response.status_code == 404


def test_proposal_returns_slots_when_booking(setup_test_db, monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test-key")
    conversation_id = _create_conversation_with_messages()

    with patch("app.api.booking.LLMService") as mock_llm_service_cls:
        mock_instance = mock_llm_service_cls.return_value
        mock_instance.classify = AsyncMock(
            return_value={"intent": "BOOKING", "confidence": 0.91}
        )

        response = client.post(
            "/booking/proposal", json={"conversation_id": conversation_id}
        )

    assert response.status_code == 200
    assert response.json() == [
        "Завтра 14:00",
        "Завтра 16:00",
        "Пятница 11:00",
    ]
    assert response.json() == PROPOSAL_SLOTS


def test_proposal_passes_conversation_history_to_llm(setup_test_db, monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test-key")
    conversation_id = _create_conversation_with_messages()

    with patch("app.api.booking.LLMService") as mock_llm_service_cls:
        mock_instance = mock_llm_service_cls.return_value
        mock_instance.classify = AsyncMock(
            return_value={"intent": "BOOKING", "confidence": 0.91}
        )

        client.post("/booking/proposal", json={"conversation_id": conversation_id})

    mock_instance.classify.assert_awaited_once()
    called_messages = mock_instance.classify.call_args[0][0]
    assert called_messages == [
        {"role": "user", "content": "I would like to come in for a haircut"},
        {"role": "assistant", "content": "Of course, when suits you?"},
    ]


@pytest.mark.parametrize(
    "intent", [intent for intent in INTENTS if intent != "BOOKING"]
)
def test_proposal_conflicts_when_intent_is_not_booking(
    setup_test_db, monkeypatch, intent
):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test-key")
    conversation_id = _create_conversation_with_messages()

    with patch("app.api.booking.LLMService") as mock_llm_service_cls:
        mock_instance = mock_llm_service_cls.return_value
        mock_instance.classify = AsyncMock(
            return_value={"intent": intent, "confidence": 0.88}
        )

        response = client.post(
            "/booking/proposal", json={"conversation_id": conversation_id}
        )

    assert response.status_code == 409
    assert response.json()["detail"] == "Intent is not BOOKING"
