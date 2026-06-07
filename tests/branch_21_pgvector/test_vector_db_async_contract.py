import inspect

from src.ragforge.providers.vector_db.base import BaseVectorDBProvider
from src.ragforge.providers.vector_db.implementations.pgvector_provider import (
    PgVectorProvider,
)
from src.ragforge.providers.vector_db.implementations.qdrant_provider import (
    QdrantProvider,
)


ASYNC_METHODS = [
    'connect',
    'disconnect',
    'collection_exists',
    'list_collections',
    'get_collection_info',
    'create_collection',
    'delete_collection',
    'delete_records',
    'insert_one',
    'insert_many',
    'search_by_vector',
]


def test_base_vector_db_provider_contract_is_async():
    for method_name in ASYNC_METHODS:
        assert inspect.iscoroutinefunction(
            getattr(BaseVectorDBProvider, method_name)
        )


def test_qdrant_provider_implements_async_contract():
    for method_name in ASYNC_METHODS:
        assert inspect.iscoroutinefunction(getattr(QdrantProvider, method_name))


def test_pgvector_provider_implements_async_contract():
    for method_name in ASYNC_METHODS:
        assert inspect.iscoroutinefunction(getattr(PgVectorProvider, method_name))
