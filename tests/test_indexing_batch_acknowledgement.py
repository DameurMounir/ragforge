from types import SimpleNamespace
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, Mock, patch

from src.ragforge.models.enums.response_signals import ResponseSignal
from src.ragforge.schemas.indexing import IndexingRequest
from src.ragforge.services import indexing_service


class IndexingBatchAcknowledgementTests(IsolatedAsyncioTestCase):
    def setUp(self):
        self.chunks = [
            SimpleNamespace(
                id=f"chunk-{i}",
                chunk_text=f"Passage {i}",
                chunk_metadata={},
                chunk_project_id="project",
                chunk_asset_id="asset",
                chunk_order=i,
            )
            for i in range(4)
        ]
        self.marked = set()
        self.vector_records = {}

        async def pending_chunks(*, only_not_embedded, **kwargs):
            self.assertTrue(only_not_embedded)
            return [chunk for chunk in self.chunks if chunk.id not in self.marked]

        async def mark(*, indexed_chunks):
            self.marked.update(item["chunk_id"] for item in indexed_chunks)
            return len(indexed_chunks)

        async def upsert(*, records, **kwargs):
            count = next(self.counts)
            if isinstance(count, Exception):
                raise count
            # A partial provider may have written any subset, including the last ID.
            if type(count) is int and 0 < count <= len(records):
                for record in records[-count:]:
                    self.vector_records[record.record_id] = record
            return count

        self.project_store = AsyncMock()
        self.project_store.get_project_by_project_id.return_value = SimpleNamespace(id="project")
        self.chunk_store = SimpleNamespace(
            get_project_chunks=AsyncMock(side_effect=pending_chunks),
            mark_chunks_embedded=AsyncMock(side_effect=mark),
        )
        self.vector_service = AsyncMock()
        self.vector_service.insert_many.side_effect = upsert
        embedding = Mock()
        embedding.embed_texts.side_effect = lambda request: SimpleNamespace(
            model="model", embeddings=[[1.0] for _ in request.texts]
        )
        settings = SimpleNamespace(
            VECTOR_DB_COLLECTION_NAME="fixture",
            EMBEDDING_MODEL="model",
            EMBEDDING_VECTOR_SIZE=1,
            EMBEDDING_PROVIDER="fixture",
            VECTOR_DB_DISTANCE="cosine",
        )
        with (
            patch.object(indexing_service.EmbeddingProviderFactory, "create_provider", return_value=embedding),
            patch.object(indexing_service, "VectorDBService", return_value=self.vector_service),
        ):
            self.service = indexing_service.IndexingService(settings)

    async def index(self, *counts, batch_size=2):
        self.counts = iter(counts)
        status, response = await self.service.index_project_chunks(
            "project",
            IndexingRequest(batch_size=batch_size, include_results=True),
            self.project_store,
            self.chunk_store,
        )
        self.assertEqual(status, 200)
        return response

    async def test_retries_only_unconfirmed_batch_with_stable_ids(self):
        response = await self.index(1, 2)
        self.assertEqual(response["signal"], ResponseSignal.INDEXING_PARTIAL_SUCCESS.value)
        self.assertEqual((response["indexed_chunks"], response["failed_chunks"]), (2, 2))
        self.assertEqual([item["chunk_id"] for item in response["results"]], ["chunk-2", "chunk-3"])
        self.assertEqual(self.marked, {"chunk-2", "chunk-3"})
        self.assertEqual(set(self.vector_records), {"chunk-1", "chunk-2", "chunk-3"})

        retry = await self.index(2)
        self.assertEqual(retry["signal"], ResponseSignal.INDEXING_SUCCESS.value)
        self.assertEqual((retry["indexed_chunks"], retry["failed_chunks"]), (2, 0))
        self.assertEqual([item["vector_id"] for item in retry["results"]], ["chunk-0", "chunk-1"])
        self.assertEqual(self.marked, {chunk.id for chunk in self.chunks})
        self.assertEqual(set(self.vector_records), self.marked)

    async def test_zero_or_invalid_count_never_marks_or_reports_vectors(self):
        self.chunks = self.chunks[:1]
        for count in (0, -1, 2, True, 1.0, None):
            with self.subTest(count=count):
                response = await self.index(count)
                self.assertEqual(response["signal"], ResponseSignal.INDEXING_FAILED.value)
                self.assertEqual((response["indexed_chunks"], response["failed_chunks"]), (0, 1))
                self.assertEqual(response["results"], [])
                self.chunk_store.mark_chunks_embedded.assert_not_awaited()

    async def test_later_exception_preserves_acknowledged_batch_for_retry(self):
        with self.assertRaisesRegex(RuntimeError, "unavailable"):
            await self.index(2, RuntimeError("unavailable"))
        self.vector_service.close.assert_awaited_once()
        self.assertEqual(self.marked, {"chunk-0", "chunk-1"})
        retry = await self.index(2)
        self.assertEqual([item["vector_id"] for item in retry["results"]], ["chunk-2", "chunk-3"])
