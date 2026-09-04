from unittest.mock import patch
import unittest

from app.ai.openai_provider import OpenAIProvider


def test_openai_provider_requires_api_key():
    with patch("app.ai.openai_provider.settings.OPENAI_API_KEY", None):
        with unittest.TestCase().assertRaisesRegex(
            ValueError, "OPENAI_API_KEY is not configured."
        ):
            OpenAIProvider()
