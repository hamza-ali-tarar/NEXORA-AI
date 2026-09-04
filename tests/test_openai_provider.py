from unittest.mock import MagicMock, patch

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
        try:
            OpenAIProvider()
            assert False, "Expected AIProviderConfigurationError was not raised."
        except AIProviderConfigurationError as exc:
            assert str(exc) == "OPENAI_API_KEY is not configured."


def test_openai_provider_generates_response():
    mock_response = MagicMock()
    mock_response.output_text = "Hello from NEXORA AI"

    mock_client = MagicMock()
    mock_client.responses.create.return_value = mock_response

    with patch(
        "app.ai.openai_provider.settings.OPENAI_API_KEY",
        "test-api-key",
    ):
        with patch(
            "app.ai.openai_provider.OpenAI",
            return_value=mock_client,
        ):
            provider = OpenAIProvider()

    response = provider.generate_response(
        "Hello NEXORA AI",
    )

    assert response == "Hello from NEXORA AI"

    mock_client.responses.create.assert_called_once_with(
        model="gpt-5-mini",
        input="Hello NEXORA AI",
    )


def test_openai_provider_generate_response_handles_request_error():
    mock_client = MagicMock()
    mock_client.responses.create.side_effect = RuntimeError(
        "OpenAI request failed"
    )

    with patch(
        "app.ai.openai_provider.settings.OPENAI_API_KEY",
        "test-api-key",
    ):
        with patch(
            "app.ai.openai_provider.OpenAI",
            return_value=mock_client,
        ):
            provider = OpenAIProvider()

    try:
        provider.generate_response("Hello NEXORA AI")
        assert False, "Expected AIProviderRequestError was not raised."
    except AIProviderRequestError as exc:
        assert str(exc) == "OpenAI provider request failed."


def test_openai_provider_generates_conversation_response():
    mock_response = MagicMock()
    mock_response.output_text = "Hello from NEXORA AI"

    mock_client = MagicMock()
    mock_client.responses.create.return_value = mock_response

    with patch(
        "app.ai.openai_provider.settings.OPENAI_API_KEY",
        "test-api-key",
    ):
        with patch(
            "app.ai.openai_provider.OpenAI",
            return_value=mock_client,
        ):
            provider = OpenAIProvider()

    messages = [
        {
            "role": "user",
            "content": "Hello NEXORA",
        },
        {
            "role": "assistant",
            "content": "Hello! How can I help?",
        },
        {
            "role": "user",
            "content": "Tell me about Python.",
        },
    ]

    response = provider.generate_conversation_response(messages)

    assert response == "Hello from NEXORA AI"

    mock_client.responses.create.assert_called_once_with(
        model="gpt-5-mini",
        input=[
            {
                "role": "user",
                "content": "Hello NEXORA",
            },
            {
                "role": "assistant",
                "content": "Hello! How can I help?",
            },
            {
                "role": "user",
                "content": "Tell me about Python.",
            },
        ],
    )


def test_openai_provider_generate_conversation_response_handles_request_error():
    mock_client = MagicMock()
    mock_client.responses.create.side_effect = RuntimeError(
        "OpenAI request failed"
    )

    with patch(
        "app.ai.openai_provider.settings.OPENAI_API_KEY",
        "test-api-key",
    ):
        with patch(
            "app.ai.openai_provider.OpenAI",
            return_value=mock_client,
        ):
            provider = OpenAIProvider()

    try:
        provider.generate_conversation_response(
            [
                {
                    "role": "user",
                    "content": "Hello NEXORA",
                },
            ]
        )
        assert False, "Expected AIProviderRequestError was not raised."
    except AIProviderRequestError as exc:
        assert str(exc) == "OpenAI provider request failed."