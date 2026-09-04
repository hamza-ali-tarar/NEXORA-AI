from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest  # type: ignore[reportMissingImports]

from app.ai.exceptions import (
    AIProviderConfigurationError,
    AIProviderRequestError,
)
from app.ai.openai_provider import OpenAIProvider


def test_openai_provider_requires_api_key():
    with patch(
        "app.ai.openai_provider.settings.OPENAI_API_KEY",
        None,
    ):
        with pytest.raises(AIProviderConfigurationError) as exc_info:
            OpenAIProvider()

    assert str(exc_info.value) == "OPENAI_API_KEY is not configured."


def test_openai_provider_generates_response():
    fake_response = SimpleNamespace(
        output_text="Hello from OpenAI.",
    )

    fake_client = Mock()
    fake_client.responses.create.return_value = fake_response

    with patch(
        "app.ai.openai_provider.settings.OPENAI_API_KEY",
        "test-api-key",
    ):
        with patch(
            "app.ai.openai_provider.OpenAI",
            return_value=fake_client,
        ):
            provider = OpenAIProvider()

    response = provider.generate_response("Hello NEXORA")

    assert response == "Hello from OpenAI."

    fake_client.responses.create.assert_called_once_with(
        model="gpt-5-mini",
        input="Hello NEXORA",
    )


def test_openai_provider_generates_conversation_response():
    fake_response = SimpleNamespace(
        output_text="Conversation response.",
    )

    fake_client = Mock()
    fake_client.responses.create.return_value = fake_response

    with patch(
        "app.ai.openai_provider.settings.OPENAI_API_KEY",
        "test-api-key",
    ):
        with patch(
            "app.ai.openai_provider.OpenAI",
            return_value=fake_client,
        ):
            provider = OpenAIProvider()

    messages = [
        {
            "role": "user",
            "content": "Hello NEXORA",
        },
        {
            "role": "assistant",
            "content": "Hello!",
        },
        {
            "role": "user",
            "content": "Tell me about Python.",
        },
    ]

    response = provider.generate_conversation_response(messages)

    assert response == "Conversation response."

    fake_client.responses.create.assert_called_once_with(
        model="gpt-5-mini",
        input=[
            {
                "role": "user",
                "content": "Hello NEXORA",
            },
            {
                "role": "assistant",
                "content": "Hello!",
            },
            {
                "role": "user",
                "content": "Tell me about Python.",
            },
        ],
    )


def test_openai_provider_converts_request_error():
    fake_client = Mock()
    fake_client.responses.create.side_effect = RuntimeError(
        "OpenAI connection failed"
    )

    with patch(
        "app.ai.openai_provider.settings.OPENAI_API_KEY",
        "test-api-key",
    ):
        with patch(
            "app.ai.openai_provider.OpenAI",
            return_value=fake_client,
        ):
            provider = OpenAIProvider()

    with pytest.raises(AIProviderRequestError) as exc_info:
        provider.generate_response("Hello NEXORA")

    assert str(exc_info.value) == "OpenAI provider request failed."


def test_openai_provider_conversation_converts_request_error():
    fake_client = Mock()
    fake_client.responses.create.side_effect = RuntimeError(
        "OpenAI connection failed"
    )

    with patch(
        "app.ai.openai_provider.settings.OPENAI_API_KEY",
        "test-api-key",
    ):
        with patch(
            "app.ai.openai_provider.OpenAI",
            return_value=fake_client,
        ):
            provider = OpenAIProvider()

    messages = [
        {
            "role": "user",
            "content": "Hello NEXORA",
        },
    ]

    with pytest.raises(AIProviderRequestError) as exc_info:
        provider.generate_conversation_response(messages)

    assert str(exc_info.value) == "OpenAI provider request failed."