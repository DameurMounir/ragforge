from abc import ABC, abstractmethod
from typing import Any

from src.ragforge.providers.vector_db.schemas import (
    VectorRecord,
    VectorSearchResult,
)


class BaseVectorDBProvider(ABC):
    """
    Abstract interface for all vector database providers.

    RAGForge services must depend on this interface, not directly on Qdrant,
    Pinecone, Weaviate, Chroma, PgVector, or any concrete implementation.
    """

    @abstractmethod
    def connect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def collection_exists(self, collection_name: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list_collections(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def get_collection_info(self, collection_name: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: str,
        do_reset: bool = False,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def delete_collection(self, collection_name: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def insert_one(
        self,
        collection_name: str,
        record: VectorRecord,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def insert_many(
        self,
        collection_name: str,
        records: list[VectorRecord],
        batch_size: int = 64,
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    def search_by_vector(
        self,
        collection_name: str,
        vector: list[float],
        limit: int = 10,
        filters: dict | None = None,
    ) -> list[VectorSearchResult]:
        raise NotImplementedError