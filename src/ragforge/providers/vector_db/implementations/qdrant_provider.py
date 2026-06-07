from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

from qdrant_client import QdrantClient, models

from src.ragforge.providers.vector_db.base import BaseVectorDBProvider
from src.ragforge.providers.vector_db.enums import DistanceMethod, QdrantMode
from src.ragforge.providers.vector_db.exceptions import (
    VectorDBConfigurationError,
    VectorDBProviderError,
)
from src.ragforge.providers.vector_db.schemas import (
    VectorRecord,
    VectorSearchResult,
)


class QdrantProvider(BaseVectorDBProvider):
    """
    Qdrant implementation of the async vector database provider interface.

    The underlying qdrant_client used by Branch 15 is synchronous. Branch 21 keeps
    Qdrant supported by exposing async methods at the RAGForge provider boundary.
    A future branch can replace this implementation with Qdrant's async client.
    """

    def __init__(
        self,
        mode: str,
        url: str,
        local_path: str,
        api_key: str | None = None,
        prefer_grpc: bool = False,
    ):
        self.mode = mode
        self.url = url
        self.local_path = local_path
        self.api_key = api_key or None
        self.prefer_grpc = prefer_grpc
        self.client: QdrantClient | None = None

    async def connect(self) -> None:
        if self.mode == QdrantMode.LOCAL.value:
            Path(self.local_path).mkdir(parents=True, exist_ok=True)
            self.client = QdrantClient(path=self.local_path)
            return

        if self.mode == QdrantMode.SERVER.value:
            self.client = QdrantClient(
                url=self.url,
                api_key=self.api_key,
                prefer_grpc=self.prefer_grpc,
            )
            return

        raise VectorDBConfigurationError(
            f'Unsupported Qdrant mode: {self.mode}'
        )

    async def disconnect(self) -> None:
        if self.client is not None and hasattr(self.client, 'close'):
            self.client.close()
        self.client = None

    def _get_client(self) -> QdrantClient:
        if self.client is None:
            raise VectorDBProviderError(
                'Qdrant client is not connected. Call connect() first.'
            )
        return self.client

    def _distance(self, distance: str) -> models.Distance:
        mapping = {
            DistanceMethod.COSINE.value: models.Distance.COSINE,
            DistanceMethod.DOT.value: models.Distance.DOT,
            DistanceMethod.EUCLID.value: models.Distance.EUCLID,
        }

        if distance not in mapping:
            raise VectorDBConfigurationError(
                f'Unsupported Qdrant distance method: {distance}'
            )

        return mapping[distance]

    def _normalize_point_id(self, record_id: str | int | None) -> str | int:
        """
        Qdrant point IDs must be integers or UUID strings.

        RAGForge record IDs may be domain IDs such as MongoDB IDs, asset IDs,
        chunk IDs, or other strings. Non-UUID strings are converted to stable
        UUIDv5 values while the original record_id is preserved in the payload.
        """

        if record_id is None:
            return str(uuid4())

        if isinstance(record_id, int):
            return record_id

        try:
            UUID(str(record_id))
            return str(record_id)
        except ValueError:
            return str(uuid5(NAMESPACE_URL, str(record_id)))

    def _build_payload(self, record: VectorRecord) -> dict[str, Any]:
        payload = dict(record.metadata or {})
        payload['text'] = record.text

        if record.record_id is not None:
            payload['record_id'] = str(record.record_id)

        return payload

    def _build_filter(self, filters: dict | None) -> models.Filter | None:
        if not filters:
            return None

        conditions = [
            models.FieldCondition(
                key=key,
                match=models.MatchValue(value=value),
            )
            for key, value in filters.items()
        ]

        return models.Filter(must=conditions)

    async def collection_exists(self, collection_name: str) -> bool:
        client = self._get_client()
        return client.collection_exists(collection_name=collection_name)

    async def list_collections(self) -> list[str]:
        client = self._get_client()
        collections = client.get_collections().collections
        return [collection.name for collection in collections]

    async def get_collection_info(self, collection_name: str) -> Any:
        client = self._get_client()
        return client.get_collection(collection_name=collection_name)

    async def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: str,
        do_reset: bool = False,
    ) -> bool:
        client = self._get_client()

        if do_reset and await self.collection_exists(collection_name):
            await self.delete_collection(collection_name=collection_name)

        if await self.collection_exists(collection_name):
            return False

        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=self._distance(distance),
            ),
        )

        return True

    async def delete_collection(self, collection_name: str) -> bool:
        client = self._get_client()

        if not await self.collection_exists(collection_name):
            return False

        client.delete_collection(collection_name=collection_name)
        return True

    async def delete_records(
        self,
        collection_name: str,
        filters: dict | None = None,
    ) -> int:
        """
        Delete vector records from Qdrant.

        Qdrant delete operations do not always expose a portable deleted count.
        To keep the provider contract useful, this implementation first scrolls
        matching point IDs, deletes them, and returns the number of IDs selected.
        """

        client = self._get_client()

        if not await self.collection_exists(collection_name):
            return 0

        qdrant_filter = self._build_filter(filters=filters)
        deleted_count = 0
        next_offset = None

        while True:
            points, next_offset = client.scroll(
                collection_name=collection_name,
                scroll_filter=qdrant_filter,
                limit=256,
                offset=next_offset,
                with_payload=False,
                with_vectors=False,
            )

            point_ids = [point.id for point in points]

            if point_ids:
                client.delete(
                    collection_name=collection_name,
                    points_selector=models.PointIdsList(
                        points=point_ids,
                    ),
                    wait=True,
                )
                deleted_count += len(point_ids)

            if next_offset is None:
                break

        return deleted_count

    async def insert_one(
        self,
        collection_name: str,
        record: VectorRecord,
    ) -> bool:
        client = self._get_client()

        if not await self.collection_exists(collection_name):
            raise VectorDBProviderError(
                f'Cannot insert into missing collection: {collection_name}'
            )

        client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=self._normalize_point_id(record.record_id),
                    vector=record.vector,
                    payload=self._build_payload(record),
                )
            ],
        )

        return True

    async def insert_many(
        self,
        collection_name: str,
        records: list[VectorRecord],
        batch_size: int = 64,
    ) -> int:
        client = self._get_client()

        if not await self.collection_exists(collection_name):
            raise VectorDBProviderError(
                f'Cannot insert into missing collection: {collection_name}'
            )

        inserted_count = 0

        for start in range(0, len(records), batch_size):
            batch = records[start : start + batch_size]
            points = [
                models.PointStruct(
                    id=self._normalize_point_id(record.record_id),
                    vector=record.vector,
                    payload=self._build_payload(record),
                )
                for record in batch
            ]

            client.upsert(
                collection_name=collection_name,
                points=points,
            )
            inserted_count += len(points)

        return inserted_count

    async def search_by_vector(
        self,
        collection_name: str,
        vector: list[float],
        limit: int = 10,
        filters: dict | None = None,
    ) -> list[VectorSearchResult]:
        client = self._get_client()

        query_response = client.query_points(
            collection_name=collection_name,
            query=vector,
            query_filter=self._build_filter(filters=filters),
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )

        points = getattr(query_response, 'points', query_response)
        normalized_results: list[VectorSearchResult] = []

        for point in points:
            payload = point.payload or {}
            text = payload.get('text')
            record_id = payload.get('record_id', point.id)
            metadata = {
                key: value
                for key, value in payload.items()
                if key not in {'text', 'record_id'}
            }

            normalized_results.append(
                VectorSearchResult(
                    record_id=record_id,
                    score=float(point.score),
                    text=text,
                    metadata=metadata,
                )
            )

        return normalized_results