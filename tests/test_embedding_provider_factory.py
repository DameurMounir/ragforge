import pytest

from src.ragforge.providers.embedding.exceptions import (
    EmbeddingConfigurationError,
)
from src.ragforge.providers.embedding.factory import EmbeddingProviderFactory
from src.ragforge.providers.embedding.implementations.fake_embedding_provider import (
    FakeEmbeddingProvider,
)
from src.ragforge.providers.embedding.schemas import EmbeddingRequest


class FakeSettings:
    EMBEDDING_PROVIDER = 'fake'
    EMBEDDING_MODEL = 'text-embedding-3-small'
    EMBEDDING_VECTOR_SIZE = 1536


class BadSettings:
    EMBEDDING_PROVIDER = 'bad_provider'


def test_embedding_factory_returns_fake_provider():
    provider = EmbeddingProviderFactory.create_provider(settings=FakeSettings())

    assert isinstance(provider, FakeEmbeddingProvider)


def test_embedding_factory_rejects_unknown_provider():
    with pytest.raises(EmbeddingConfigurationError):
        EmbeddingProviderFactory.create_provider(settings=BadSettings())


def test_fake_embedding_provider_returns_expected_dimensions():
    provider = EmbeddingProviderFactory.create_provider(settings=FakeSettings())

    response = provider.embed_texts(
        EmbeddingRequest(texts=['hello world'])
    )

    assert len(response.embeddings) == 1
    assert len(response.embeddings[0]) == 1536
