from collections.abc import Sequence

from openai import OpenAI  # pyright: ignore[reportMissingImports]

from app.ai.provider import AIProvider
from app.core.config import settings


class OpenAIProvider(AIProvider):
    """OpenAI-backed implementation of the NEXORA AI provider."""

    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured.")

        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
        )

    def generate_response(self, prompt: str) -> str:
        """Generate a response from a single text prompt."""

        response = self.client.responses.create(
            model="gpt-5-mini",
            input=prompt,
        )

        return response.output_text

    def generate_conversation_response(
        self,
        messages: Sequence[dict[str, str]],
    ) -> str:
        """Generate a response using structured conversation messages."""

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

        return response.output_text
