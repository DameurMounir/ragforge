import pytest

from src.ragforge.providers.vector_db.exceptions import VectorDBConfigurationError


@pytest.mark.anyio
async def test_hnsw_index_sql_uses_configured_dimension_and_operator(
    make_capturing_pgvector_provider,
):
    provider, session_manager = make_capturing_pgvector_provider(
        vector_size=384,
        distance='cosine',
        index_type='hnsw',
        index_vector_type='vector',
        hnsw_m=32,
        hnsw_ef_construction=128,
    )

    created = await provider._ensure_vector_index()

    assert created is True
    sql_text = '\n'.join(sql for sql, _ in session_manager.session_obj.executed)
    assert 'USING hnsw' in sql_text
    assert 'embedding::vector(384)' in sql_text
    assert 'vector_cosine_ops' in sql_text
    assert 'WITH (m = 32, ef_construction = 128)' in sql_text
    assert 'WHERE vector_size = 384' in sql_text


@pytest.mark.anyio
async def test_ivfflat_index_is_not_created_before_min_records(
    make_capturing_pgvector_provider,
):
    provider, session_manager = make_capturing_pgvector_provider(
        configured_record_count=10,
        index_type='ivfflat',
        index_min_records=100,
    )

    created = await provider._ensure_vector_index()

    assert created is False
    sql_text = '\n'.join(sql for sql, _ in session_manager.session_obj.executed)
    assert 'SELECT COUNT(*)' in sql_text
    assert 'CREATE INDEX' not in sql_text


@pytest.mark.anyio
async def test_ivfflat_index_sql_uses_lists_after_threshold(
    make_capturing_pgvector_provider,
):
    provider, session_manager = make_capturing_pgvector_provider(
        configured_record_count=250,
        index_type='ivfflat',
        ivfflat_lists=50,
        index_min_records=100,
    )

    created = await provider._ensure_vector_index()

    assert created is True
    sql_text = '\n'.join(sql for sql, _ in session_manager.session_obj.executed)
    assert 'USING ivfflat' in sql_text
    assert 'WITH (lists = 50)' in sql_text


def test_index_vector_type_must_support_configured_dimension(make_pgvector_provider):
    with pytest.raises(VectorDBConfigurationError):
        make_pgvector_provider(vector_size=5000, index_vector_type='halfvec')


def test_auto_create_index_can_be_disabled(make_pgvector_provider):
    provider = make_pgvector_provider(auto_create_index=False)
    assert provider.auto_create_index is False
