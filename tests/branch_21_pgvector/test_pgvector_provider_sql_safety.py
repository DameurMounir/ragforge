import pytest

from src.ragforge.providers.vector_db.exceptions import (
    VectorDBConfigurationError,
    VectorDBProviderError,
)


def test_pgvector_rejects_unsafe_table_name(make_pgvector_provider):
    with pytest.raises(VectorDBConfigurationError):
        make_pgvector_provider(table_name='vector_records; DROP TABLE projects;')


def test_pgvector_rejects_unsafe_metadata_filter_key(make_pgvector_provider):
    provider = make_pgvector_provider()
    with pytest.raises(VectorDBProviderError):
        provider._build_filter_clause({'project_id; DROP TABLE assets;': 'x'})


def test_pgvector_uses_logical_collection_not_dynamic_table_name(make_pgvector_provider):
    provider = make_pgvector_provider()
    assert provider.table_name == 'vector_records'
    assert provider._index_name() == 'ix_vector_records_embedding_hnsw_cosine_vector_384'


def test_pgvector_supports_configured_vector_size_without_code_change(
    make_pgvector_provider,
):
    provider = make_pgvector_provider(vector_size=768)
    assert provider.vector_size == 768
    assert 'vector(768)' in provider._typed_embedding_expression()


def test_pgvector_supports_halfvec_index_expression_without_code_change(
    make_pgvector_provider,
):
    provider = make_pgvector_provider(
        vector_size=3072,
        index_vector_type='halfvec',
    )
    assert provider.vector_size == 3072
    assert 'halfvec(3072)' in provider._typed_embedding_expression()
    assert provider._operator_class() == 'halfvec_cosine_ops'


def test_pgvector_rejects_vector_index_above_supported_dimensions(
    make_pgvector_provider,
):
    with pytest.raises(VectorDBConfigurationError):
        make_pgvector_provider(vector_size=3072, index_vector_type='vector')


def test_pgvector_rejects_missing_vector_size(make_pgvector_provider):
    with pytest.raises(VectorDBConfigurationError):
        make_pgvector_provider(vector_size=None)


def test_pgvector_supports_configured_distance_modes(make_pgvector_provider):
    assert make_pgvector_provider(distance='cosine')._distance_operator() == '<=>'
    assert make_pgvector_provider(distance='euclid')._distance_operator() == '<->'
    assert make_pgvector_provider(distance='dot')._distance_operator() == '<#>'


def test_pgvector_rejects_unknown_distance_mode(make_pgvector_provider):
    with pytest.raises(VectorDBConfigurationError):
        make_pgvector_provider(distance='unknown')
