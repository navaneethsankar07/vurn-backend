class AIServiceError(Exception):
    """Base exception for AI integration errors."""


class AIConfigurationError(AIServiceError):
    pass


class AIProviderError(AIServiceError):
    pass


class AIProviderTimeoutError(AIProviderError):
    pass


class AIResponseError(AIServiceError):
    pass


class AIStructuredOutputError(AIResponseError):
    pass


class AICreditError(AIServiceError):
    """Base exception for AI credit management errors."""


class UnsupportedAIFeatureError(AICreditError):
    pass


class InvalidAICreditCostError(AICreditError):
    pass
