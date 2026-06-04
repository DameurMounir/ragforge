from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

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
    Qdrant implementation of the vector database provider interface.

    This provider is the only place where Qdrant-specific client logic should
    exist. Services must use VectorDBService instead of calling Qdrant directly.
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

    def connect(self) -> None:
        """
        Connect to Qdrant using the configured mode.

        Supported modes:
        - local: embedded/local Qdrant storage
        - server: remote or Docker Qdrant server
        """
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

    def disconnect(self) -> None:
        """
        Disconnect the provider client.

        QdrantClient does not require an explicit network close for the current
        use case, so we remove the client reference.
        """
        self.client = None

    def _get_client(self) -> QdrantClient:
        """
        Return the active Qdrant client or fail clearly if not connected.
        """
        if self.client is None:
            raise VectorDBProviderError(
                'Qdrant client is not connected. Call connect() first.'
            )

        return self.client

    def _distance(self, distance: str) -> models.Distance:
        """
        Map RAGForge distance enum values to Qdrant distance values.
        """
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
        Normalize RAGForge record IDs into Qdrant-compatible point IDs.

        Qdrant point IDs must be integers or UUID strings. MongoDB ObjectId
        strings are not UUID strings, so arbitrary string IDs are converted into
        stable UUIDv5 values.

        The original RAGForge record ID is preserved inside the payload as
        `record_id` so search results can still return the real chunk/vector ID.
        """
        if record_id is None:
            return str(uuid5(NAMESPACE_URL, 'ragforge-auto-generated-id'))

        if isinstance(record_id, int):
            return record_id

        try:
            UUID(str(record_id))
            return str(record_id)
        except ValueError:
            return str(uuid5(NAMESPACE_URL, str(record_id)))

    def _build_payload(self, record: VectorRecord) -> dict[str, Any]:
        """
        Build a Qdrant payload from a VectorRecord.

        Payload strategy:
        - metadata is stored flat at the top level to make filtering simple;
        - text is stored as a top-level field;
        - original record_id is stored as a top-level field.

        This allows Branch 17 to filter by project_id / asset_id and still
        rebuild source metadata for Branch 18 citations.
        """
        payload = dict(record.metadata or {})
        payload['text'] = record.text

        if record.record_id is not None:
            payload['record_id'] = str(record.record_id)

        return payload

    def _build_filter(self, filters: dict | None) -> models.Filter | None:
        """
        Build a Qdrant metadata filter from a simple dictionary.

        Example:
        {'project_id': '...', 'asset_id': '...'}
        """
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

    def collection_exists(self, collection_name: str) -> bool:
        client = self._get_client()
        return client.collection_exists(collection_name=collection_name)

    def list_collections(self) -> list[str]:
        client = self._get_client()
        collections = client.get_collections().collections
        return [collection.name for collection in collections]

    def get_collection_info(self, collection_name: str) -> Any:
        client = self._get_client()
        return client.get_collection(collection_name=collection_name)

    def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: str,
        do_reset: bool = False,
    ) -> bool:
        client = self._get_client()

        if do_reset and self.collection_exists(collection_name):
            self.delete_collection(collection_name=collection_name)

        if self.collection_exists(collection_name):
            return False

        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=self._distance(distance),
            ),
        )

        return True

    def delete_collection(self, collection_name: str) -> bool:
        client = self._get_client()

        if not self.collection_exists(collection_name):
            return False

        client.delete_collection(collection_name=collection_name)
        return True

    def insert_one(
        self,
        collection_name: str,
        record: VectorRecord,
    ) -> bool:
        client = self._get_client()

        if not self.collection_exists(collection_name):
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

    def insert_many(
        self,
        collection_name: str,
        records: list[VectorRecord],
        batch_size: int = 64,
    ) -> int:
        client = self._get_client()

        if not self.collection_exists(collection_name):
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

    def search_by_vector(
        self,
        collection_name: str,
        vector: list[float],
        limit: int = 10,
        filters: dict | None = None,
    ) -> list[VectorSearchResult]:
        """
        Search vectors by query vector and return provider-neutral results.

        Important:
        `_build_payload()` stores metadata flat at Qdrant payload level.
        Therefore, search result normalization must rebuild metadata by removing
        internal fields: `text` and `record_id`.

        This is what makes Branch 17 source-ready for Branch 18:
        search results now expose chunk_id, asset_id, project_id, chunk_order,
        and all other metadata needed for citations.
        """
        client = self._get_client()

        query_response = client.query_points(
            collection_name=collection_name,
            query=vector,
            query_filter=self._build_filter(filters),
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
