from .provider import AIProvider


class MockAIProvider(AIProvider):
    """Deterministic AI provider used for development and testing."""

    def generate_response(self, prompt: str) -> str:
        return f"Mock response: {prompt}"