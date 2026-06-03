from http import HTTPStatus

from src.ragforge.models.enums.response_signals import ResponseSignal
from src.ragforge.providers.embedding.factory import EmbeddingProviderFactory
from src.ragforge.providers.embedding.schemas import EmbeddingRequest
from src.ragforge.providers.vector_db.schemas import VectorRecord
from src.ragforge.schemas.indexing import (
    IndexedChunkResult,
    IndexingRequest,
)
from src.ragforge.services.base_service import BaseService
from src.ragforge.services.vector_db_service import VectorDBService
from src.ragforge.stores.mongodb.chunk_store import ChunkStore
from src.ragforge.stores.mongodb.project_store import ProjectStore


class IndexingService(BaseService):
    """
    Branch 16 indexing orchestration service.

    Current implemented strategy:
    DataChunk -> Embedding -> Vector DB Point

    Future-ready strategies:
    - late_chunking
    - contextual chunking
    - asset summary indexing
    - hierarchical retrieval

    Important architectural rule:
    this service depends on VectorDBService, not directly on Qdrant.
    """

    def __init__(self, settings: object):
        super().__init__()
        self.settings = settings
        self.embedding_provider = EmbeddingProviderFactory.create_provider(
            settings=settings
        )
        self.vector_db_service = VectorDBService(settings=settings)

    async def index_project_chunks(
        self,
        project_id: str,
        indexing_request: IndexingRequest,
        project_store: ProjectStore,
        chunk_store: ChunkStore,
    ) -> tuple[int, dict]:
        """
        Index stored MongoDB chunks into the configured vector database.

        Branch 16 scope:
        - read DataChunk records from MongoDB,
        - generate embeddings,
        - insert vectors into the configured vector DB,
        - mark chunks as embedded.

        This service does not perform semantic search.
        """

        project = await project_store.get_project_by_project_id(
            project_id=project_id
        )

        if project is None or project.id is None:
            return int(HTTPStatus.NOT_FOUND), {
                'signal': ResponseSignal.PROJECT_NOT_FOUND.value,
                'message': 'Project not found.',
                'project_id': project_id,
            }

        chunks = await chunk_store.get_project_chunks(
            project_id=project.id,
            asset_id=indexing_request.asset_id,
            only_not_embedded=not indexing_request.do_reset,
            limit=indexing_request.limit,
        )

        if not chunks:
            return int(HTTPStatus.BAD_REQUEST), {
                'signal': ResponseSignal.NO_CHUNKS_TO_INDEX.value,
                'message': 'No chunks found to index.',
                'project_id': project_id,
                'asset_id': indexing_request.asset_id,
            }

        collection_name = self.settings.VECTOR_DB_COLLECTION_NAME
        requested_embedding_model = self.settings.EMBEDDING_MODEL
        actual_embedding_model = requested_embedding_model
        vector_size = self.settings.EMBEDDING_VECTOR_SIZE
        vector_distance = self.settings.VECTOR_DB_DISTANCE
        batch_size = indexing_request.batch_size

        indexed_results: list[IndexedChunkResult] = []
        failed_chunks = 0
        skipped_chunks = 0
        chunks_to_mark: list[dict] = []

        self.vector_db_service.connect()

        try:
            self.vector_db_service.ensure_collection(
                collection_name=collection_name,
                vector_size=vector_size,
                distance=vector_distance,
                do_reset=False,
            )

            for start in range(0, len(chunks), batch_size):
                batch_chunks = chunks[start : start + batch_size]

                valid_chunks = [
                    chunk
                    for chunk in batch_chunks
                    if chunk.id is not None and str(chunk.chunk_text).strip()
                ]

                skipped_chunks += len(batch_chunks) - len(valid_chunks)

                if not valid_chunks:
                    continue

                texts = [
                    chunk.chunk_text
                    for chunk in valid_chunks
                ]

                embedding_response = self.embedding_provider.embed_texts(
                    EmbeddingRequest(
                        texts=texts,
                        model=requested_embedding_model,
                    )
                )

                actual_embedding_model = embedding_response.model

                if len(embedding_response.embeddings) != len(valid_chunks):
                    failed_chunks += len(valid_chunks)
                    continue

                vector_records: list[VectorRecord] = []

                for chunk, embedding in zip(
                    valid_chunks,
                    embedding_response.embeddings,
                    strict=True,
                ):
                    vector_id = str(chunk.id)

                    payload = {
                        'project_id': str(chunk.chunk_project_id),
                        'asset_id': str(chunk.chunk_asset_id),
                        'chunk_id': str(chunk.id),
                        'chunk_order': chunk.chunk_order,
                        'index_level': 'chunk',
                        'indexing_strategy': indexing_request.strategy.value,
                        'source_type': 'data_chunk',
                        'embedding_model': embedding_response.model,
                    }

                    payload.update(chunk.chunk_metadata or {})

                    vector_records.append(
                        VectorRecord(
                            record_id=vector_id,
                            vector=embedding,
                            text=chunk.chunk_text,
                            metadata=payload,
                        )
                    )

                    indexed_results.append(
                        IndexedChunkResult(
                            chunk_id=str(chunk.id),
                            asset_id=str(chunk.chunk_asset_id),
                            vector_id=vector_id,
                            chunk_order=chunk.chunk_order,
                            embedding_model=embedding_response.model,
                        )
                    )

                    chunks_to_mark.append(
                        {
                            'chunk_id': chunk.id,
                            'embedding_model': embedding_response.model,
                            'vector_id': vector_id,
                        }
                    )

                inserted_count = self.vector_db_service.insert_many(
                    collection_name=collection_name,
                    records=vector_records,
                    batch_size=batch_size,
                )

                if inserted_count != len(vector_records):
                    failed_chunks += len(vector_records) - inserted_count

            if chunks_to_mark:
                await chunk_store.mark_chunks_embedded(
                    indexed_chunks=chunks_to_mark
                )

        finally:
            self.vector_db_service.close()

        indexed_chunks = len(indexed_results)

        if indexed_chunks > 0 and failed_chunks > 0:
            signal = ResponseSignal.INDEXING_PARTIAL_SUCCESS.value
        elif indexed_chunks > 0:
            signal = ResponseSignal.INDEXING_SUCCESS.value
        else:
            signal = ResponseSignal.INDEXING_FAILED.value

        response = {
            'signal': signal,
            'message': 'Indexing completed.',
            'project_id': project_id,
            'asset_id': indexing_request.asset_id,
            'strategy': indexing_request.strategy.value,
            'granularity': indexing_request.granularity.value,
            'collection_name': collection_name,
            'embedding_model': actual_embedding_model,
            'indexed_chunks': indexed_chunks,
            'failed_chunks': failed_chunks,
            'skipped_chunks': skipped_chunks,
        }

        if indexing_request.include_results:
            response['results'] = [
                result.model_dump()
                for result in indexed_results
            ]

        return int(HTTPStatus.OK), response