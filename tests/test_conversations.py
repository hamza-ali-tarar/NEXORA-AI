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