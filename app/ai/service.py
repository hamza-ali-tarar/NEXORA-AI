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
    ) -> str:
        """Generate an AI response using conversation history as context."""

        conversation_text = "\n".join(
            f"{message['role']}: {message['content']}"
            for message in messages
        )

        return self.provider.generate_response(
            conversation_text,
        )
