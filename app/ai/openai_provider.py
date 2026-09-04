from collections.abc import Sequence

from openai import OpenAI  # pyright: ignore[reportMissingImports]

from app.ai.exceptions import (
    AIProviderConfigurationError,
    AIProviderRequestError,
)
from app.ai.provider import AIProvider
from app.core.config import settings


class OpenAIProvider(AIProvider):
    """OpenAI-backed implementation of the NEXORA AI provider."""

    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            raise AIProviderConfigurationError(
                "OPENAI_API_KEY is not configured."
            )

        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
        )

    def generate_response(self, prompt: str) -> str:
        """Generate a response from a single text prompt."""

        try:
            response = self.client.responses.create(
                model="gpt-5-mini",
                input=prompt,
            )
        except Exception as exc:
            raise AIProviderRequestError(
                "OpenAI provider request failed."
            ) from exc

        return response.output_text

    def generate_conversation_response(
        self,
        messages: Sequence[dict[str, str]],
    ) -> str:
        """Generate a response using structured conversation messages."""

        try:
            response = self.client.responses.create(
                model="gpt-5-mini",
                input=[
                    {
                        "role": message["role"],
                        "content": message["content"],
                    }
                    for message in messages
                ],
            )
        except Exception as exc:
            raise AIProviderRequestError(
                "OpenAI provider request failed."
            ) from exc

        return response.output_text