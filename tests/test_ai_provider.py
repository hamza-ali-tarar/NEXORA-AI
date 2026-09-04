import sys
from pathlib import Path

from collections.abc import Sequence


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ai.provider import AIProvider


def test_ai_provider_is_abstract():
    assert AIProvider.__abstractmethods__ == {
        "generate_response",
        "generate_conversation_response",
    }


def test_ai_provider_requires_conversation_response_implementation():
    class IncompleteProvider(AIProvider):
        def generate_response(self, prompt: str) -> str:
            return "response"

    assert "generate_conversation_response" in (
        IncompleteProvider.__abstractmethods__
    )


def test_ai_provider_can_be_implemented():
    class CompleteProvider(AIProvider):
        def generate_response(self, prompt: str) -> str:
            return "response"

        def generate_conversation_response(
            self,
            messages: Sequence[dict[str, str]],
        ) -> str:
            return "conversation response"

    provider = CompleteProvider()

    assert provider.generate_response("Hello") == "response"
    assert provider.generate_conversation_response(
        [{"role": "user", "content": "Hello"}]
    ) == "conversation response"