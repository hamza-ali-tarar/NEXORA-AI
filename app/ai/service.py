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

        conversation_text = "\n".join(
            f"{message['role']}: {message['content']}"
            for message in messages
        )

        if knowledge_context:
            prompt = (
                "Relevant knowledge:\n"
                f"{knowledge_context}\n\n"
                "Conversation:\n"
                f"{conversation_text}"
            )
        else:
            prompt = conversation_text

        return self.provider.generate_response(prompt)