from unittest.mock import patch

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


def test_ai_chat_endpoint(client: TestClient):
    token = register_and_login(
        client,
        "ai-endpoint@nexora.ai",
    )

    conversation_response = client.post(
        "/api/v1/conversations/",
        headers=auth_headers(token),
        json={"title": "AI Endpoint Test"},
    )

    assert conversation_response.status_code == 201

    conversation_id = conversation_response.json()["id"]

    with patch(
        "app.api.v1.ai.OpenAIProvider.generate_response",
        return_value="Mocked AI response",
    ):
        response = client.post(
            "/api/v1/ai/chat",
            headers=auth_headers(token),
            json={
                "conversation_id": conversation_id,
                "message": "Hello NEXORA AI",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["conversation_id"] == conversation_id
    assert data["user_message"] == "Hello NEXORA AI"
    assert data["assistant_message"] == "Mocked AI response"


def test_ai_chat_requires_existing_conversation(client: TestClient):
    token = register_and_login(
        client,
        "ai-missing-conversation@nexora.ai",
    )

    with patch(
        "app.api.v1.ai.OpenAIProvider.generate_response",
        return_value="Mocked AI response",
    ):
        response = client.post(
            "/api/v1/ai/chat",
            headers=auth_headers(token),
            json={
                "conversation_id": 999999,
                "message": "Hello NEXORA AI",
            },
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Conversation not found."