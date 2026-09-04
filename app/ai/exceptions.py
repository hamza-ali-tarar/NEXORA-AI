class AIProviderError(Exception):
    """Base exception for AI provider failures."""


class AIProviderConfigurationError(AIProviderError):
    """Raised when an AI provider is not configured correctly."""


class AIProviderRequestError(AIProviderError):
    """Raised when an AI provider request fails."""