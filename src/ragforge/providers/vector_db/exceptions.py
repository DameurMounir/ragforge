class VectorDBError(Exception):
    """
    Base exception for vector database provider errors.
    """


class VectorDBConfigurationError(VectorDBError):
    """
    Raised when vector DB configuration is invalid or incomplete.
    """


class VectorDBProviderError(VectorDBError):
    """
    Raised when a vector DB provider operation fails.
    """