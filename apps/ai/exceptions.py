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
