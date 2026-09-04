from collections.abc import Sequence

from app.ai.service import AIService


class FakeProvider:
    def __init__(self):
        self.last_prompt: str | None = None
        self.last_messages: list[dict[str, str]] | None = None

    def generate_response(self, prompt: str) -> str:
        self.last_prompt = prompt
        return f"AI: {prompt}"

    def generate_conversation_response(
        self,
        messages: Sequence[dict[str, str]],
    ) -> str:
        self.last_messages = list(messages)

        conversation = "\n".join(
            f"{message['role']}: {message['content']}"
            for message in messages
        )

        return f"AI: {conversation}"


def test_ai_service_generates_response():
    provider = FakeProvider()
    service = AIService(provider=provider)

    response = service.generate_response("Hello NEXORA")

    assert response == "AI: Hello NEXORA"
    assert provider.last_prompt == "Hello NEXORA"


def test_ai_service_generates_conversation_response():
    provider = FakeProvider()
    service = AIService(provider=provider)

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

    assert provider.last_messages == messages


def test_ai_service_adds_knowledge_as_system_message():
    provider = FakeProvider()
    service = AIService(provider=provider)

    messages = [
        {
            "role": "user",
            "content": "Tell me about Python.",
        },
    ]

    response = service.generate_conversation_response(
        messages,
        knowledge_context="Python is a programming language.",
    )

    assert response == (
        "AI: system: Use the following relevant knowledge when "
        "answering the conversation:\n\n"
        "Python is a programming language.\n"
        "user: Tell me about Python."
    )

    assert provider.last_messages is not None
    assert provider.last_messages[0] == {
        "role": "system",
        "content": (
            "Use the following relevant knowledge when "
            "answering the conversation:\n\n"
            "Python is a programming language."
        ),
    }


def test_ai_service_does_not_mutate_original_messages():
    provider = FakeProvider()
    service = AIService(provider=provider)

    messages = [
        {
            "role": "user",
            "content": "Hello NEXORA",
        },
    ]

    original_messages = [message.copy() for message in messages]

    service.generate_conversation_response(
        messages,
        knowledge_context="Some knowledge.",
    )

    assert messages == original_messages


def test_ai_service_without_knowledge_preserves_message_order():
    provider = FakeProvider()
    service = AIService(provider=provider)

    messages = [
        {
            "role": "user",
            "content": "First message",
        },
        {
            "role": "assistant",
            "content": "Second message",
        },
        {
            "role": "user",
            "content": "Third message",
        },
    ]

    service.generate_conversation_response(messages)

    assert provider.last_messages == messages