from collections.abc import Sequence

from .provider import AIProvider


class AIService:
    """Application service responsible for generating AI responses."""

    def __init__(self, provider: AIProvider):
        self.provider = provider

    def generate_response(self, prompt: str) -> str:
        return self.provider.generate_response(prompt)

    def generate_conversation_response(
        self,
        messages: Sequence[dict[str, str]],
        knowledge_context: str | None = None,
    ) -> str:
        """Generate an AI response using conversation and knowledge context."""

        conversation_messages = list(messages)

        if knowledge_context:
            conversation_messages.insert(
                0,
                {
                    "role": "system",
                    "content": (
                        "Use the following relevant knowledge when "
                        "answering the conversation:\n\n"
                        f"{knowledge_context}"
                    ),
                },
            )

        return self.provider.generate_conversation_response(
            conversation_messages,
        )