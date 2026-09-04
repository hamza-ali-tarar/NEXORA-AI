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
    token = register_and_login(client, "ai-endpoint@nexora.ai")

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


def test_ai_chat_uses_conversation_history(client: TestClient):
    token = register_and_login(
        client,
        "ai-history@nexora.ai",
    )

    conversation_response = client.post(
        "/api/v1/conversations/",
        headers=auth_headers(token),
        json={"title": "AI History Test"},
    )

    assert conversation_response.status_code == 201

    conversation_id = conversation_response.json()["id"]

    first_message_response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages/",
        headers=auth_headers(token),
        json={
            "role": "user",
            "content": "My name is NEXORA.",
        },
    )

    assert first_message_response.status_code == 201

    assistant_message_response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages/",
        headers=auth_headers(token),
        json={
            "role": "assistant",
            "content": "Nice to meet you, NEXORA.",
        },
    )

    assert assistant_message_response.status_code == 201

    captured_messages: list[dict[str, str]] = []

    def fake_generate_response(prompt: str) -> str:
        captured_messages.append(
            {
                "role": "context",
                "content": prompt,
            }
        )

        return "I remember that you said your name is NEXORA."

    with patch(
        "app.api.v1.ai.OpenAIProvider.generate_response",
        side_effect=fake_generate_response,
    ):
        response = client.post(
            "/api/v1/ai/chat",
            headers=auth_headers(token),
            json={
                "conversation_id": conversation_id,
                "message": "Do you remember my name?",
            },
        )

    assert response.status_code == 200
    assert len(captured_messages) == 1

    prompt = captured_messages[0]["content"]

    assert "user: My name is NEXORA." in prompt
    assert "assistant: Nice to meet you, NEXORA." in prompt
    assert "user: Do you remember my name?" in prompt

    data = response.json()

    assert data["assistant_message"] == (
        "I remember that you said your name is NEXORA."
    )


def test_ai_chat_uses_relevant_knowledge(client: TestClient):
    token = register_and_login(
        client,
        "ai-knowledge@nexora.ai",
    )

    knowledge_response = client.post(
        "/api/v1/knowledge/",
        headers=auth_headers(token),
        json={
            "title": "Python Knowledge",
            "content": (
                "Python is a high-level programming language "
                "used for software development and automation."
            ),
        },
    )

    assert knowledge_response.status_code == 201

    conversation_response = client.post(
        "/api/v1/conversations/",
        headers=auth_headers(token),
        json={"title": "Knowledge AI Test"},
    )

    assert conversation_response.status_code == 201

    conversation_id = conversation_response.json()["id"]

    captured_prompts: list[str] = []

    def fake_generate_response(prompt: str) -> str:
        captured_prompts.append(prompt)

        return "Python is a high-level programming language."

    with patch(
        "app.api.v1.ai.OpenAIProvider.generate_response",
        side_effect=fake_generate_response,
    ):
        response = client.post(
            "/api/v1/ai/chat",
            headers=auth_headers(token),
            json={
                "conversation_id": conversation_id,
                "message": "Tell me about Python.",
            },
        )

    assert response.status_code == 200
    assert len(captured_prompts) == 1

    prompt = captured_prompts[0]

    assert "Relevant knowledge:" in prompt
    assert "Title: Python Knowledge" in prompt
    assert (
        "Python is a high-level programming language "
        "used for software development and automation."
    ) in prompt
    assert "Conversation:" in prompt
    assert "user: Tell me about Python." in prompt

    data = response.json()

    assert data["assistant_message"] == (
        "Python is a high-level programming language."
    )
