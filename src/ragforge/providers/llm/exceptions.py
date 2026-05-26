class LLMError(Exception):
    """
    Base exception for LLM provider errors.
    """


class LLMConfigurationError(LLMError):
    """
    Raised when provider configuration is invalid or incomplete.
    """


class LLMProviderError(LLMError):
    """
    Raised when an external provider fails during generation.
    """