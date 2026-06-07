from abc import ABC, abstractmethod
from typing import Any

from src.ragforge.providers.vector_db.schemas import (
    VectorRecord,
    VectorSearchResult,
)


class BaseVectorDBProvider(ABC):
    """
    Async abstract interface for all vector database providers.

    Branch 21 upgrades the vector DB boundary to async because PgVector uses
    SQLAlchemy async sessions. Qdrant remains supported through async wrappers
    around its current synchronous client calls.
    """

    @abstractmethod
    async def connect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def disconnect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def collection_exists(self, collection_name: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def list_collections(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    async def get_collection_info(self, collection_name: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: str,
        do_reset: bool = False,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def delete_collection(self, collection_name: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def delete_records(
        self,
        collection_name: str,
        filters: dict | None = None,
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    async def insert_one(
        self,
        collection_name: str,
        record: VectorRecord,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def insert_many(
        self,
        collection_name: str,
        records: list[VectorRecord],
        batch_size: int = 64,
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    async def search_by_vector(
        self,
        collection_name: str,
        vector: list[float],
        limit: int = 10,
        filters: dict | None = None,
    ) -> list[VectorSearchResult]:
        raise NotImplementedError
