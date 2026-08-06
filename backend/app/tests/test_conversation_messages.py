import uuid

from app.tests.testdb import client


def _create_conversation() -> int:
    unique_phone = f"+6{uuid.uuid4().int % 10**9:09d}"
    client.post(
        "/clients",
        json={"first_name": "History", "last_name": "Tester", "phone": unique_phone},
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

    return conversation["id"]


def test_get_messages_conversation_not_found(setup_test_db):
    response = client.get("/conversations/999999/messages")

    assert response.status_code == 404


def test_get_messages_empty_conversation(setup_test_db):
    conversation_id = _create_conversation()

    response = client.get(f"/conversations/{conversation_id}/messages")

    assert response.status_code == 200
    assert response.json() == []


def test_get_messages_returns_history_in_created_at_order(setup_test_db):
    conversation_id = _create_conversation()

    contents = ["first", "second", "third"]
    for index, content in enumerate(contents):
        client.post(
            f"/conversations/{conversation_id}/messages",
            json={
                "channel": "whatsapp",
                "direction": "inbound" if index % 2 == 0 else "outbound",
                "content": content,
            },
        )

    response = client.get(f"/conversations/{conversation_id}/messages")

    assert response.status_code == 200
    messages = response.json()
    assert [m["content"] for m in messages] == contents
    assert [m["direction"] for m in messages] == ["inbound", "outbound", "inbound"]
    assert all(m["conversation_id"] == conversation_id for m in messages)
    assert all(m["created_at"] for m in messages)


def test_get_messages_is_scoped_to_one_conversation(setup_test_db):
    first_id = _create_conversation()
    second_id = _create_conversation()

    client.post(
        f"/conversations/{first_id}/messages",
        json={"channel": "whatsapp", "direction": "inbound", "content": "belongs to first"},
    )
    client.post(
        f"/conversations/{second_id}/messages",
        json={"channel": "whatsapp", "direction": "inbound", "content": "belongs to second"},
    )

    first = client.get(f"/conversations/{first_id}/messages").json()
    second = client.get(f"/conversations/{second_id}/messages").json()

    assert [m["content"] for m in first] == ["belongs to first"]
    assert [m["content"] for m in second] == ["belongs to second"]
