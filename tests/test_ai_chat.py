from unittest.mock import patch

from fastapi.testclient import TestClient

from app.ai.exceptions import (
    AIProviderConfigurationError,
    AIProviderRequestError,
)


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


def create_conversation(
    client: TestClient,
    token: str,
    title: str,
) -> int:
    response = client.post(
        "/api/v1/conversations/",
        headers=auth_headers(token),
        json={"title": title},
    )

    assert response.status_code == 201

    return response.json()["id"]


def test_ai_chat_endpoint(client: TestClient):
    token = register_and_login(client, "ai-endpoint@nexora.ai")

    conversation_id = create_conversation(
        client,
        token,
        "AI Endpoint Test",
    )

    with patch(
        "app.api.v1.ai.OpenAIProvider.generate_conversation_response",
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
        "app.api.v1.ai.OpenAIProvider.generate_conversation_response",
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

    conversation_id = create_conversation(
        client,
        token,
        "AI History Test",
    )

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

    captured_messages: list[list[dict[str, str]]] = []

    def fake_generate_conversation_response(
        messages: list[dict[str, str]],
    ) -> str:
        captured_messages.append(messages)

        return "I remember that you said your name is NEXORA."

    with patch(
        "app.api.v1.ai.OpenAIProvider.generate_conversation_response",
        side_effect=fake_generate_conversation_response,
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

    messages = captured_messages[0]

    assert messages[0] == {
        "role": "user",
        "content": "My name is NEXORA.",
    }

    assert messages[1] == {
        "role": "assistant",
        "content": "Nice to meet you, NEXORA.",
    }

    assert messages[2] == {
        "role": "user",
        "content": "Do you remember my name?",
    }

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

    conversation_id = create_conversation(
        client,
        token,
        "Knowledge AI Test",
    )

    captured_messages: list[list[dict[str, str]]] = []

    def fake_generate_conversation_response(
        messages: list[dict[str, str]],
    ) -> str:
        captured_messages.append(messages)

        return "Python is a high-level programming language."

    with patch(
        "app.api.v1.ai.OpenAIProvider.generate_conversation_response",
        side_effect=fake_generate_conversation_response,
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
    assert len(captured_messages) == 1

    messages = captured_messages[0]

    assert "relevant knowledge" in messages[0]["content"].lower()
    assert messages[0]["role"] == "system"
    assert "Title: Python Knowledge" in messages[0]["content"]
    assert (
        "Python is a high-level programming language "
        "used for software development and automation."
    ) in messages[0]["content"]

    assert messages[-1] == {
        "role": "user",
        "content": "Tell me about Python.",
    }

    data = response.json()

    assert data["assistant_message"] == (
        "Python is a high-level programming language."
    )


def test_ai_chat_does_not_use_other_users_knowledge(client: TestClient):
    user_a_token = register_and_login(
        client,
        "ai-security-user-a@nexora.ai",
    )

    user_b_token = register_and_login(
        client,
        "ai-security-user-b@nexora.ai",
    )

    knowledge_response = client.post(
        "/api/v1/knowledge/",
        headers=auth_headers(user_a_token),
        json={
            "title": "Private Secret Knowledge",
            "content": (
                "This information belongs only to User A "
                "and must never be exposed to another user."
            ),
        },
    )

    assert knowledge_response.status_code == 201

    conversation_id = create_conversation(
        client,
        user_b_token,
        "Security Test",
    )

    captured_messages: list[list[dict[str, str]]] = []

    def fake_generate_conversation_response(
        messages: list[dict[str, str]],
    ) -> str:
        captured_messages.append(messages)

        return "I do not have that information."

    with patch(
        "app.api.v1.ai.OpenAIProvider.generate_conversation_response",
        side_effect=fake_generate_conversation_response,
    ):
        response = client.post(
            "/api/v1/ai/chat",
            headers=auth_headers(user_b_token),
            json={
                "conversation_id": conversation_id,
                "message": "Tell me about private secret knowledge.",
            },
        )

    assert response.status_code == 200
    assert len(captured_messages) == 1

    combined_content = "\n".join(
        message["content"]
        for message in captured_messages[0]
    )

    assert "Private Secret Knowledge" not in combined_content
    assert "This information belongs only to User A" not in combined_content

    data = response.json()

    assert data["assistant_message"] == (
        "I do not have that information."
    )


def test_ai_chat_returns_503_for_provider_configuration_error(
    client: TestClient,
):
    token = register_and_login(
        client,
        "ai-config-error@nexora.ai",
    )

    conversation_id = create_conversation(
        client,
        token,
        "Configuration Error Test",
    )

    with patch(
        "app.api.v1.ai.OpenAIProvider",
        side_effect=AIProviderConfigurationError(
            "OPENAI_API_KEY is not configured."
        ),
    ):
        response = client.post(
            "/api/v1/ai/chat",
            headers=auth_headers(token),
            json={
                "conversation_id": conversation_id,
                "message": "Hello NEXORA AI",
            },
        )

    assert response.status_code == 503
    assert response.json()["detail"] == "AI provider is not configured."

    messages_response = client.get(
        f"/api/v1/conversations/{conversation_id}/messages/",
        headers=auth_headers(token),
    )

    assert messages_response.status_code == 200
    assert messages_response.json() == []


def test_ai_chat_returns_502_for_provider_request_error(
    client: TestClient,
):
    token = register_and_login(
        client,
        "ai-request-error@nexora.ai",
    )

    conversation_id = create_conversation(
        client,
        token,
        "Provider Request Error Test",
    )

    with patch(
        "app.api.v1.ai.OpenAIProvider.generate_conversation_response",
        side_effect=AIProviderRequestError(
            "OpenAI provider request failed."
        ),
    ):
        response = client.post(
            "/api/v1/ai/chat",
            headers=auth_headers(token),
            json={
                "conversation_id": conversation_id,
                "message": "Hello NEXORA AI",
            },
        )

    assert response.status_code == 502
    assert response.json()["detail"] == "AI provider request failed."

    messages_response = client.get(
        f"/api/v1/conversations/{conversation_id}/messages/",
        headers=auth_headers(token),
    )

    assert messages_response.status_code == 200
    assert messages_response.json() == []


def test_ai_chat_returns_500_for_unexpected_error(
    client: TestClient,
):
    token = register_and_login(
        client,
        "ai-unexpected-error@nexora.ai",
    )

    conversation_id = create_conversation(
        client,
        token,
        "Unexpected Error Test",
    )

    with patch(
        "app.api.v1.ai.KnowledgeRetrievalService.search",
        side_effect=RuntimeError("Unexpected database failure"),
    ):
        response = client.post(
            "/api/v1/ai/chat",
            headers=auth_headers(token),
            json={
                "conversation_id": conversation_id,
                "message": "Hello NEXORA AI",
            },
        )

    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error."

    messages_response = client.get(
        f"/api/v1/conversations/{conversation_id}/messages/",
        headers=auth_headers(token),
    )

    assert messages_response.status_code == 200
    assert messages_response.json() == []