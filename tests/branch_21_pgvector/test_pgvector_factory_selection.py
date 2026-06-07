import inspect

import pytest

from src.ragforge.providers.vector_db.exceptions import VectorDBConfigurationError
from src.ragforge.providers.vector_db.factory import VectorDBProviderFactory
from src.ragforge.providers.vector_db.implementations.pgvector_provider import (
    PgVectorProvider,
)
from src.ragforge.providers.vector_db.implementations.qdrant_provider import (
    QdrantProvider,
)

from .conftest import (
    BadProviderSettings,
    ConflictingPgVectorSettings,
    IncompletePgVectorSettings,
    PgVectorSettings,
    QdrantSettings,
)


def test_vector_db_factory_returns_qdrant_provider():
    provider = VectorDBProviderFactory.create_provider(settings=QdrantSettings())
    assert isinstance(provider, QdrantProvider)


def test_vector_db_factory_returns_pgvector_provider_and_uses_effective_size():
    settings = PgVectorSettings()
    provider = VectorDBProviderFactory.create_provider(settings=settings)
    assert isinstance(provider, PgVectorProvider)
    assert provider.vector_size == settings.EMBEDDING_VECTOR_SIZE


def test_vector_db_factory_rejects_unknown_provider():
    with pytest.raises(VectorDBConfigurationError):
        VectorDBProviderFactory.create_provider(settings=BadProviderSettings())


def test_vector_db_factory_does_not_hide_fallback_defaults():
    source = inspect.getsource(VectorDBProviderFactory.create_provider)
    assert 'getattr(' not in source
    assert "'hnsw'" not in source
    assert '1536' not in source


def test_pgvector_dimension_conflict_fails_before_provider_creation():
    with pytest.raises(ValueError):
        VectorDBProviderFactory.create_provider(
            settings=ConflictingPgVectorSettings()
        )


def test_pgvector_missing_config_fails_fast():
    with pytest.raises(AttributeError):
        VectorDBProviderFactory.create_provider(
            settings=IncompletePgVectorSettings()
        )
