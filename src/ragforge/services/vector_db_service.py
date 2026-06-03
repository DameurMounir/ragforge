from src.ragforge.providers.vector_db.factory import VectorDBProviderFactory
from src.ragforge.providers.vector_db.schemas import (
    VectorRecord,
    VectorSearchResult,
)


class VectorDBService:
    """
    Provider-neutral service layer for vector database operations.

    This service must not depend on Qdrant-specific configuration names.
    It only uses generic vector DB settings from core/config.py.
    """

    def __init__(self, settings: object):
        self.settings = settings
        self.provider = VectorDBProviderFactory.create_provider(
            settings=settings
        )

    def connect(self) -> None:
        self.provider.connect()

    def close(self) -> None:
        self.provider.disconnect()

    def ensure_default_collection(self, do_reset: bool = False) -> bool:
        return self.ensure_collection(
            collection_name=self.settings.VECTOR_DB_COLLECTION_NAME,
            vector_size=self.settings.VECTOR_DB_VECTOR_SIZE,
            distance=self.settings.VECTOR_DB_DISTANCE,
            do_reset=do_reset,
        )

    def ensure_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: str,
        do_reset: bool = False,
    ) -> bool:
        return self.provider.create_collection(
            collection_name=collection_name,
            vector_size=vector_size,
            distance=distance,
            do_reset=do_reset,
        )

    def insert_one(
        self,
        collection_name: str,
        record: VectorRecord,
    ) -> bool:
        return self.provider.insert_one(
            collection_name=collection_name,
            record=record,
        )

    def insert_many(
        self,
        collection_name: str,
        records: list[VectorRecord],
        batch_size: int = 64,
    ) -> int:
        return self.provider.insert_many(
            collection_name=collection_name,
            records=records,
            batch_size=batch_size,
        )

    def search_by_vector(
        self,
        collection_name: str,
        vector: list[float],
        limit: int = 10,
        filters: dict | None = None,
    ) -> list[VectorSearchResult]:
        return self.provider.search_by_vector(
            collection_name=collection_name,
            vector=vector,
            limit=limit,
            filters=filters,
        )

    def delete_collection(self, collection_name: str) -> bool:
        return self.provider.delete_collection(collection_name=collection_name)
