import pytest

from src.ragforge.providers.vector_db.exceptions import (
    VectorDBConfigurationError,
)
from src.ragforge.providers.vector_db.factory import VectorDBProviderFactory
from src.ragforge.providers.vector_db.implementations.qdrant_provider import (
    QdrantProvider,
)


class DummySettings:
    VECTOR_DB_PROVIDER = 'qdrant'
    QDRANT_MODE = 'local'
    QDRANT_URL = 'http://localhost:6333'
    QDRANT_API_KEY = None
    QDRANT_LOCAL_PATH = 'storage/vector_db/test_qdrant'
    QDRANT_PREFER_GRPC = False


class BadSettings:
    VECTOR_DB_PROVIDER = 'unknown_provider'


def test_vector_db_factory_returns_qdrant_provider():
    provider = VectorDBProviderFactory.create_provider(settings=DummySettings())

    assert isinstance(provider, QdrantProvider)


def test_vector_db_factory_rejects_unknown_provider():
    with pytest.raises(VectorDBConfigurationError):
        VectorDBProviderFactory.create_provider(settings=BadSettings())