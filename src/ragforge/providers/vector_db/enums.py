from enum import Enum


class VectorDBProvider(str, Enum):
    """
    Supported vector database providers.

    QDRANT is the first implementation for Branch 15.
    """

    QDRANT = 'qdrant'


class QdrantMode(str, Enum):
    """
    Qdrant execution modes.

    SERVER: connect to a running Qdrant service, usually Docker.
    LOCAL: use embedded local Qdrant storage for tests/prototyping.
    """

    SERVER = 'server'
    LOCAL = 'local'


class DistanceMethod(str, Enum):
    """
    Supported vector distance methods.
    """

    COSINE = 'cosine'
    DOT = 'dot'
    EUCLID = 'euclid'