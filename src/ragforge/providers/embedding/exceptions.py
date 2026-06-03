class EmbeddingError(Exception):
    """
    Base exception for embedding provider errors.
    """


class EmbeddingConfigurationError(EmbeddingError):
    """
    Raised when embedding configuration is invalid.
    """


class EmbeddingProviderError(EmbeddingError):
    """
    Raised when an embedding provider operation fails.
    """
