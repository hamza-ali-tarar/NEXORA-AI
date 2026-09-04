from app.ai.openai_provider import OpenAIProvider
from app.ai.provider import AIProvider


def get_ai_provider() -> AIProvider:
    """Return the configured AI provider for the application."""

    return OpenAIProvider()