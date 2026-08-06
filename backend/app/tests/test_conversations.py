import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.db.database import get_db
from app.core.config import settings


# Create test database (use same database for testing)
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


def test_create_conversation(setup_test_db):
    # First, create a client
    client.post(
        "/clients",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+1234567890",
        },
    )

    # Get the client ID
    response = client.get("/clients")
    assert response.status_code == 200
    clients = response.json()
    assert len(clients) > 0
    client_id = clients[0]["id"]

    # Create a conversation
    response = client.post(
        "/conversations",
        json={
            "customer_id": client_id,
            "primary_channel": "whatsapp",
            "current_channel": "whatsapp",
            "status": "active",
        },
    )
    assert response.status_code == 200
    conversation = response.json()
    assert conversation["customer_id"] == client_id
    assert conversation["primary_channel"] == "whatsapp"
    assert conversation["current_channel"] == "whatsapp"
    assert conversation["status"] == "active"
    assert "id" in conversation
    assert "created_at" in conversation
    assert "updated_at" in conversation


def test_get_conversations(setup_test_db):
    response = client.get("/conversations")
    assert response.status_code == 200
    conversations = response.json()
    assert isinstance(conversations, list)


def test_get_conversation_by_id(setup_test_db):
    # Create a client and conversation first
    client_response = client.post(
        "/clients",
        json={
            "first_name": "Jane",
            "last_name": "Smith",
            "phone": "+9876543210",
        },
    )

    clients = client.get("/clients").json()
    client_id = clients[-1]["id"]

    conv_response = client.post(
        "/conversations",
        json={
            "customer_id": client_id,
            "primary_channel": "telegram",
            "current_channel": "telegram",
            "status": "pending",
        },
    )
    conversation_id = conv_response.json()["id"]

    # Get the conversation
    response = client.get(f"/conversations/{conversation_id}")
    assert response.status_code == 200
    conversation = response.json()
    assert conversation["id"] == conversation_id
    assert conversation["customer_id"] == client_id


def test_get_conversation_not_found(setup_test_db):
    response = client.get("/conversations/9999")
    assert response.status_code == 404


def test_create_message(setup_test_db):
    # Create client and conversation
    clients = client.get("/clients").json()
    if not clients:
        client.post(
            "/clients",
            json={
                "first_name": "Test",
                "last_name": "User",
                "phone": "+1111111111",
            },
        )
        clients = client.get("/clients").json()

    client_id = clients[0]["id"]

    conv_response = client.post(
        "/conversations",
        json={
            "customer_id": client_id,
            "primary_channel": "email",
            "current_channel": "email",
            "status": "open",
        },
    )
    conversation_id = conv_response.json()["id"]

    # Create a message
    response = client.post(
        f"/conversations/{conversation_id}/messages",
        json={
            "channel": "email",
            "direction": "outbound",
            "content": "Hello, this is a test message",
        },
    )
    assert response.status_code == 200
    message = response.json()
    assert message["conversation_id"] == conversation_id
    assert message["channel"] == "email"
    assert message["direction"] == "outbound"
    assert message["content"] == "Hello, this is a test message"
    assert "id" in message
    assert "created_at" in message


def test_create_message_conversation_not_found(setup_test_db):
    response = client.post(
        "/conversations/9999/messages",
        json={
            "channel": "sms",
            "direction": "inbound",
            "content": "test",
        },
    )
    assert response.status_code == 404
