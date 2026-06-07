from src.ragforge.providers.vector_db.factory import VectorDBProviderFactory
from src.ragforge.providers.vector_db.schemas import (
    VectorRecord,
    VectorSearchResult,
)


class VectorDBService:
    """
    Provider-neutral service layer for vector database operations.

    Branch 21 makes this service async so both Qdrant and PgVector share the same
    service contract without leaking provider-specific implementation details.
    """

    def __init__(self, settings: object):
        self.settings = settings
        self.provider = VectorDBProviderFactory.create_provider(settings=settings)

    async def connect(self) -> None:
        await self.provider.connect()

    async def close(self) -> None:
        await self.provider.disconnect()

    async def ensure_default_collection(self, do_reset: bool = False) -> bool:
        return await self.ensure_collection(
            collection_name=self.settings.VECTOR_DB_COLLECTION_NAME,
            vector_size=self.settings.EMBEDDING_VECTOR_SIZE,
            distance=self.settings.VECTOR_DB_DISTANCE,
            do_reset=do_reset,
        )

    async def ensure_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: str,
        do_reset: bool = False,
    ) -> bool:
        return await self.provider.create_collection(
            collection_name=collection_name,
            vector_size=vector_size,
            distance=distance,
            do_reset=do_reset,
        )

    async def insert_one(
        self,
        collection_name: str,
        record: VectorRecord,
    ) -> bool:
        return await self.provider.insert_one(
            collection_name=collection_name,
            record=record,
        )

    async def insert_many(
        self,
        collection_name: str,
        records: list[VectorRecord],
        batch_size: int = 64,
    ) -> int:
        return await self.provider.insert_many(
            collection_name=collection_name,
            records=records,
            batch_size=batch_size,
        )

    async def search_by_vector(
        self,
        collection_name: str,
        vector: list[float],
        limit: int = 10,
        filters: dict | None = None,
    ) -> list[VectorSearchResult]:
        return await self.provider.search_by_vector(
            collection_name=collection_name,
            vector=vector,
            limit=limit,
            filters=filters,
        )

    async def delete_collection(self, collection_name: str) -> bool:
        return await self.provider.delete_collection(collection_name=collection_name)

    async def delete_records(
        self,
        collection_name: str,
        filters: dict | None = None,
    ) -> int:
        return await self.provider.delete_records(
            collection_name=collection_name,
            filters=filters,
        )
