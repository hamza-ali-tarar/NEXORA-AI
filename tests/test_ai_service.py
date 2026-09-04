import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ai.mock_provider import MockAIProvider
from app.ai.service import AIService


def test_ai_service_generates_response():
    service = AIService(provider=MockAIProvider())

    response = service.generate_response("Hello NEXORA")

    assert response == "Mock response: Hello NEXORA"


def test_ai_service_uses_provider():
    class FakeProvider:
        def generate_response(self, prompt: str) -> str:
            return f"AI: {prompt}"

    service = AIService(provider=FakeProvider())

    response = service.generate_response("Hello NEXORA")

    assert response == "AI: Hello NEXORA"


def test_ai_service_generates_conversation_response():
    class FakeProvider:
        def generate_response(self, prompt: str) -> str:
            return f"AI: {prompt}"

    service = AIService(provider=FakeProvider())

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

    response = service.generate_conversation_response(messages)

    assert response == (
        "AI: user: Hello NEXORA\n"
        "assistant: Hello! How can I help?\n"
        "user: Tell me about Python."
    )
