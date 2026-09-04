from abc import ABC, abstractmethod
from collections.abc import Sequence


class AIProvider(ABC):
    """Base interface for all NEXORA AI language-model providers."""

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """Generate an AI response from a text prompt."""
        raise NotImplementedError

    @abstractmethod
    def generate_conversation_response(
        self,
        messages: Sequence[dict[str, str]],
    ) -> str:
        """Generate an AI response from structured conversation messages."""
        raise NotImplementedError