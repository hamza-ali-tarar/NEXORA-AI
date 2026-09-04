from collections.abc import Sequence

from .provider import AIProvider


class MockAIProvider(AIProvider):
    """Deterministic AI provider used for development and testing."""

    def generate_response(self, prompt: str) -> str:
        return f"Mock response: {prompt}"

    def generate_conversation_response(
        self,
        messages: Sequence[dict[str, str]],
    ) -> str:
        conversation_text = "\n".join(
            f"{message['role']}: {message['content']}"
            for message in messages
        )

        return f"Mock response: {conversation_text}"