import pytest

from src.ragforge.providers.vector_db.exceptions import (
    VectorDBConfigurationError,
    VectorDBProviderError,
)
from src.ragforge.providers.vector_db.schemas import VectorRecord, VectorSearchResult


def test_vector_record_requires_non_empty_vector():
    with pytest.raises(ValueError):
        VectorRecord(record_id='x', vector=[], text='valid text')


def test_vector_record_requires_non_empty_text():
    with pytest.raises(ValueError):
        VectorRecord(record_id='x', vector=[0.1, 0.2], text='   ')


def test_vector_search_result_has_provider_neutral_shape():
    result = VectorSearchResult(
        record_id='chunk-1',
        score=0.91,
        text='evidence text',
        metadata={'chunk_id': 'chunk-1'},
    )
    assert result.record_id == 'chunk-1'
    assert result.score == 0.91
    assert result.metadata['chunk_id'] == 'chunk-1'


def test_pgvector_provider_requires_record_id(make_pgvector_provider):
    provider = make_pgvector_provider(vector_size=2)
    record = VectorRecord(record_id=None, vector=[0.1, 0.2], text='text')
    with pytest.raises(VectorDBProviderError):
        provider._row_from_record('ragforge_chunks', record)


def test_pgvector_provider_validates_configured_vector_length(make_pgvector_provider):
    provider = make_pgvector_provider(vector_size=4)
    with pytest.raises(VectorDBProviderError):
        provider._vector_to_pg_literal([0.1, 0.2, 0.3])


def test_pgvector_provider_rejects_invalid_index_type(make_pgvector_provider):
    with pytest.raises(VectorDBConfigurationError):
        make_pgvector_provider(index_type='flat_index_that_does_not_exist')
