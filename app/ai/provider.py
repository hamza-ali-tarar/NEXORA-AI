from abc import ABC, abstractmethod


class AIProvider(ABC):
    """Base interface for all NEXORA AI language-model providers."""

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """Generate an AI response from a text prompt."""
        raise NotImplementedError