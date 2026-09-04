from fastapi import HTTPException, status

from app.ai.mock_provider import MockAIProvider
from app.ai.openai_provider import OpenAIProvider
from app.ai.provider import AIProvider
from app.core.config import settings


def get_ai_provider() -> AIProvider:
    """Return the configured AI provider for the application."""

    provider_name = settings.AI_PROVIDER.lower()

    if provider_name == "openai":
        return OpenAIProvider()

    if provider_name == "mock":
        return MockAIProvider()

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Unsupported AI provider: {settings.AI_PROVIDER}",
    )