import pytest

from .conftest import (
    ConflictingPgVectorSettings,
    PgVectorExplicitSizeSettings,
    PgVectorSettings,
)


def test_embedding_vector_size_is_source_of_truth_when_pgvector_size_is_not_set():
    settings = PgVectorSettings()
    assert settings.PGVECTOR_VECTOR_SIZE is None
    assert settings.PGVECTOR_EFFECTIVE_VECTOR_SIZE == settings.EMBEDDING_VECTOR_SIZE


def test_explicit_pgvector_size_is_allowed_only_when_equal_to_embedding_size():
    settings = PgVectorExplicitSizeSettings()
    assert settings.PGVECTOR_VECTOR_SIZE == settings.EMBEDDING_VECTOR_SIZE
    assert settings.PGVECTOR_EFFECTIVE_VECTOR_SIZE == settings.EMBEDDING_VECTOR_SIZE


def test_conflicting_pgvector_size_is_rejected():
    settings = ConflictingPgVectorSettings()
    with pytest.raises(ValueError):
        _ = settings.PGVECTOR_EFFECTIVE_VECTOR_SIZE


def test_vector_db_vector_size_is_not_part_of_branch_21_policy():
    settings = PgVectorSettings()
    assert not hasattr(settings, 'VECTOR_DB_VECTOR_SIZE')
