from src.ragforge.providers.vector_db.base import BaseVectorDBProvider
from src.ragforge.providers.vector_db.enums import VectorDBProvider
from src.ragforge.providers.vector_db.exceptions import VectorDBConfigurationError
from src.ragforge.providers.vector_db.implementations.pgvector_provider import (
    PgVectorProvider,
)
from src.ragforge.providers.vector_db.implementations.qdrant_provider import (
    QdrantProvider,
)
from src.ragforge.stores.postgres.session import PostgresSessionManager


class VectorDBProviderFactory:
    """
    Factory responsible for creating vector DB providers from validated settings.

    Branch 21 v4 rule:
    - no provider defaults live in the factory
    - no getattr fallback values
    - every provider setting must already be normalized by core/config.py
    """

    @staticmethod
    def create_provider(settings: object) -> BaseVectorDBProvider:
        provider_value = settings.VECTOR_DB_PROVIDER

        try:
            selected_provider = VectorDBProvider(str(provider_value))
        except ValueError as error:
            raise VectorDBConfigurationError(
                f'Unsupported vector DB provider: {provider_value}'
            ) from error

        if selected_provider == VectorDBProvider.QDRANT:
            return QdrantProvider(
                mode=settings.QDRANT_MODE,
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
                local_path=settings.QDRANT_LOCAL_PATH,
                prefer_grpc=settings.QDRANT_PREFER_GRPC,
            )

        if selected_provider == VectorDBProvider.PGVECTOR:
            return PgVectorProvider(
                session_manager=PostgresSessionManager.from_settings(settings),
                table_name=settings.PGVECTOR_TABLE_NAME,
                vector_size=settings.PGVECTOR_EFFECTIVE_VECTOR_SIZE,
                distance=settings.PGVECTOR_DISTANCE,
                index_type=settings.PGVECTOR_INDEX_TYPE,
                index_vector_type=settings.PGVECTOR_INDEX_VECTOR_TYPE,
                hnsw_m=settings.PGVECTOR_HNSW_M,
                hnsw_ef_construction=settings.PGVECTOR_HNSW_EF_CONSTRUCTION,
                hnsw_ef_search=settings.PGVECTOR_HNSW_EF_SEARCH,
                ivfflat_lists=settings.PGVECTOR_IVFFLAT_LISTS,
                ivfflat_probes=settings.PGVECTOR_IVFFLAT_PROBES,
                index_min_records=settings.PGVECTOR_INDEX_MIN_RECORDS,
                auto_create_index=settings.PGVECTOR_AUTO_CREATE_INDEX,
                create_extension_on_startup=settings.PGVECTOR_CREATE_EXTENSION_ON_STARTUP,
                embedding_model=settings.EMBEDDING_MODEL,
                embedding_provider=settings.EMBEDDING_PROVIDER,
            )

        raise VectorDBConfigurationError(
            f'Unsupported vector DB provider: {selected_provider}'
        )
