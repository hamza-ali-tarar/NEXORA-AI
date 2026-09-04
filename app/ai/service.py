from .provider import AIProvider


class AIService:
    """Application service responsible for generating AI responses."""

    def __init__(self, provider: AIProvider):
        self.provider = provider

    def generate_response(self, prompt: str) -> str:
        return self.provider.generate_response(prompt)