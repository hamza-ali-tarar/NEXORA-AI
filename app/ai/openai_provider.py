from openai import OpenAI  # pyright: ignore[reportMissingImports]

from app.core.config import settings
from app.ai.provider import AIProvider


class OpenAIProvider(AIProvider):
    """OpenAI-backed implementation of the NEXORA AI provider."""

    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured.")

        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
        )

    def generate_response(self, prompt: str) -> str:
        response = self.client.responses.create(
            model="gpt-5-mini",
            input=prompt,
        )

        return response.output_text