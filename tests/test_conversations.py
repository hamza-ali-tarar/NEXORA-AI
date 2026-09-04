from fastapi.testclient import TestClient


def register_and_login(client: TestClient, email: str) -> str:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "TestPassword123!",
            "full_name": "Test User",
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "TestPassword123!",
        },
    )

    assert login_response.status_code == 200

    return login_response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_create_conversation(client: TestClient):
    token = register_and_login(client, "conversation-create@nexora.ai")

    response = client.post(
        "/api/v1/conversations/",
        headers=auth_headers(token),
        json={"title": "My First Conversation"},
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "My First Conversation"
    assert "id" in data
    assert "user_id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_list_conversations(client: TestClient):
    token = register_and_login(client, "conversation-list@nexora.ai")

    client.post(
        "/api/v1/conversations/",
        headers=auth_headers(token),
        json={"title": "Conversation One"},
    )

    client.post(
        "/api/v1/conversations/",
        headers=auth_headers(token),
        json={"title": "Conversation Two"},
    )

    response = client.get(
        "/api/v1/conversations/",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["title"] == "Conversation Two"
    assert data[1]["title"] == "Conversation One"


def test_get_conversation(client: TestClient):
    token = register_and_login(client, "conversation-get@nexora.ai")

    create_response = client.post(
        "/api/v1/conversations/",
        headers=auth_headers(token),
        json={"title": "Conversation Details"},
    )

    conversation_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/conversations/{conversation_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json()["id"] == conversation_id
    assert response.json()["title"] == "Conversation Details"


def test_get_nonexistent_conversation(client: TestClient):
    token = register_and_login(client, "conversation-notfound@nexora.ai")

    response = client.get(
        "/api/v1/conversations/999999",
        headers=auth_headers(token),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Conversation not found."


def test_conversation_ownership_isolation(client: TestClient):
    user_one_token = register_and_login(
        client,
        "conversation-owner-one@nexora.ai",
    )

    user_two_token = register_and_login(
        client,
        "conversation-owner-two@nexora.ai",
    )

    create_response = client.post(
        "/api/v1/conversations/",
        headers=auth_headers(user_one_token),
        json={"title": "Private Conversation"},
    )

    conversation_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/conversations/{conversation_id}",
        headers=auth_headers(user_two_token),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Conversation not found."


def test_delete_conversation(client: TestClient):
    token = register_and_login(client, "conversation-delete@nexora.ai")

    create_response = client.post(
        "/api/v1/conversations/",
        headers=auth_headers(token),
        json={"title": "Delete Me"},
    )

    conversation_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/conversations/{conversation_id}",
        headers=auth_headers(token),
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/api/v1/conversations/{conversation_id}",
        headers=auth_headers(token),
    )

    assert get_response.status_code == 404


def test_delete_other_users_conversation(client: TestClient):
    user_one_token = register_and_login(
        client,
        "conversation-delete-owner@nexora.ai",
    )

    user_two_token = register_and_login(
        client,
        "conversation-delete-other@nexora.ai",
    )

    create_response = client.post(
        "/api/v1/conversations/",
        headers=auth_headers(user_one_token),
        json={"title": "Protected Conversation"},
    )

    conversation_id = create_response.json()["id"]

    response = client.delete(
        f"/api/v1/conversations/{conversation_id}",
        headers=auth_headers(user_two_token),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Conversation not found."

def test_create_message(client: TestClient):
    token = register_and_login(client, "message-create@nexora.ai")

    conversation_response = client.post(
        "/api/v1/conversations/",
        headers=auth_headers(token),
        json={"title": "Message Test"},
    )

    assert conversation_response.status_code == 201

    conversation_id = conversation_response.json()["id"]

    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages/",
        headers=auth_headers(token),
        json={
            "role": "user",
            "content": "Hello NEXORA AI",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["conversation_id"] == conversation_id
    assert data["role"] == "user"
    assert data["content"] == "Hello NEXORA AI"
    assert "id" in data
    assert "created_at" in data


def test_list_messages(client: TestClient):
    token = register_and_login(client, "message-list@nexora.ai")

    conversation_response = client.post(
        "/api/v1/conversations/",
        headers=auth_headers(token),
        json={"title": "Message List Test"},
    )

    conversation_id = conversation_response.json()["id"]

    client.post(
        f"/api/v1/conversations/{conversation_id}/messages/",
        headers=auth_headers(token),
        json={
            "role": "user",
            "content": "First message",
        },
    )

    client.post(
        f"/api/v1/conversations/{conversation_id}/messages/",
        headers=auth_headers(token),
        json={
            "role": "assistant",
            "content": "Second message",
        },
    )

    response = client.get(
        f"/api/v1/conversations/{conversation_id}/messages/",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["content"] == "First message"
    assert data[1]["content"] == "Second message"


def test_message_conversation_ownership_isolation(client: TestClient):
    user_one_token = register_and_login(
        client,
        "message-owner-one@nexora.ai",
    )

    user_two_token = register_and_login(
        client,
        "message-owner-two@nexora.ai",
    )

    conversation_response = client.post(
        "/api/v1/conversations/",
        headers=auth_headers(user_one_token),
        json={"title": "Private Message Conversation"},
    )

    conversation_id = conversation_response.json()["id"]

    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages/",
        headers=auth_headers(user_two_token),
        json={
            "role": "user",
            "content": "Unauthorized message",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Conversation not found."


def test_list_messages_ownership_isolation(client: TestClient):
    user_one_token = register_and_login(
        client,
        "message-list-owner@nexora.ai",
    )

    user_two_token = register_and_login(
        client,
        "message-list-other@nexora.ai",
    )

    conversation_response = client.post(
        "/api/v1/conversations/",
        headers=auth_headers(user_one_token),
        json={"title": "Private Messages"},
    )

    conversation_id = conversation_response.json()["id"]

    response = client.get(
        f"/api/v1/conversations/{conversation_id}/messages/",
        headers=auth_headers(user_two_token),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Conversation not found."
def test_message_updates_conversation_timestamp(client: TestClient):
    token = register_and_login(
        client,
        "message-timestamp@nexora.ai",
    )

    conversation_response = client.post(
        "/api/v1/conversations/",
        headers=auth_headers(token),
        json={"title": "Timestamp Test"},
    )

    assert conversation_response.status_code == 201

    conversation_id = conversation_response.json()["id"]
    original_updated_at = conversation_response.json()["updated_at"]

    message_response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages/",
        headers=auth_headers(token),
        json={
            "role": "user",
            "content": "This should update the conversation timestamp.",
        },
    )

    assert message_response.status_code == 201

    conversation_after_message = client.get(
        f"/api/v1/conversations/{conversation_id}",
        headers=auth_headers(token),
    )

    assert conversation_after_message.status_code == 200

    new_updated_at = conversation_after_message.json()["updated_at"]

    assert new_updated_at != original_updated_at