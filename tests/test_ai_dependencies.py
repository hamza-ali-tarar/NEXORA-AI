from fastapi import HTTPException

from app.ai.dependencies import get_ai_provider
from app.ai.mock_provider import MockAIProvider
from app.ai.openai_provider import OpenAIProvider
from app.core.config import settings


def test_get_ai_provider_returns_openai_provider(monkeypatch):
    monkeypatch.setattr(settings, "AI_PROVIDER", "openai")

    provider = get_ai_provider()

    assert isinstance(provider, OpenAIProvider)


def test_get_ai_provider_returns_mock_provider(monkeypatch):
    monkeypatch.setattr(settings, "AI_PROVIDER", "mock")

    provider = get_ai_provider()

    assert isinstance(provider, MockAIProvider)


def test_get_ai_provider_rejects_unsupported_provider(monkeypatch):
    monkeypatch.setattr(settings, "AI_PROVIDER", "unsupported")

    try:
        get_ai_provider()
        assert False, "Expected unsupported AI provider to fail."
    except HTTPException as exc:
        assert exc.status_code == 500
        assert "Unsupported AI provider" in str(exc.detail)