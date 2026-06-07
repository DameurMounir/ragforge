from http import HTTPStatus

from src.ragforge.models.enums.response_signals import ResponseSignal
from src.ragforge.providers.embedding.factory import EmbeddingProviderFactory
from src.ragforge.providers.embedding.schemas import EmbeddingRequest
from src.ragforge.schemas.search import SearchEvidence, SemanticSearchRequest
from src.ragforge.services.base_service import BaseService
from src.ragforge.services.vector_db_service import VectorDBService
from src.ragforge.stores.mongodb.project_store import ProjectStore


class SemanticSearchService(BaseService):
    """
    Query -> embedding -> vector DB search -> ranked evidence.

    Branch 21 keeps this service provider-neutral and awaits vector DB calls.
    """

    def __init__(self, settings: object):
        super().__init__()
        self.settings = settings
        self.embedding_provider = EmbeddingProviderFactory.create_provider(
            settings=settings
        )
        self.vector_db_service = VectorDBService(settings=settings)

    async def search_project_chunks(
        self,
        project_id: str,
        search_request: SemanticSearchRequest,
        project_store: ProjectStore,
    ) -> tuple[int, dict]:
        project = await project_store.get_project_by_project_id(
            project_id=project_id
        )
        if project is None or project.id is None:
            return int(HTTPStatus.NOT_FOUND), {
                'signal': ResponseSignal.PROJECT_NOT_FOUND.value,
                'message': 'Project not found.',
                'project_id': project_id,
            }

        limit = (
            search_request.limit
            if search_request.limit is not None
            else self.settings.SEARCH_DEFAULT_LIMIT
        )
        if limit > self.settings.SEARCH_MAX_LIMIT:
            return int(HTTPStatus.BAD_REQUEST), {
                'signal': ResponseSignal.SEMANTIC_SEARCH_FAILED.value,
                'message': (
                    'Search limit exceeds maximum allowed value: '
                    f'{self.settings.SEARCH_MAX_LIMIT}.'
                ),
                'project_id': project_id,
                'query': search_request.query,
            }

        min_score = (
            search_request.min_score
            if search_request.min_score is not None
            else self.settings.SEARCH_MIN_SCORE
        )
        include_text = (
            search_request.include_text
            if search_request.include_text is not None
            else self.settings.SEARCH_INCLUDE_TEXT_DEFAULT
        )
        include_metadata = (
            search_request.include_metadata
            if search_request.include_metadata is not None
            else self.settings.SEARCH_INCLUDE_METADATA_DEFAULT
        )

        embedding_response = self.embedding_provider.embed_texts(
            EmbeddingRequest(
                texts=[search_request.query],
                model=self.settings.EMBEDDING_MODEL,
            )
        )
        query_vector = embedding_response.embeddings[0]
        actual_embedding_model = embedding_response.model

        filters = {'project_id': str(project.id)}
        if search_request.asset_id is not None:
            filters['asset_id'] = search_request.asset_id

        collection_name = self.settings.VECTOR_DB_COLLECTION_NAME

        await self.vector_db_service.connect()
        try:
            vector_results = await self.vector_db_service.search_by_vector(
                collection_name=collection_name,
                vector=query_vector,
                limit=limit,
                filters=filters,
            )
        finally:
            await self.vector_db_service.close()

        evidence_results: list[SearchEvidence] = []
        for result in vector_results:
            if min_score is not None and result.score < min_score:
                continue

            metadata = result.metadata or {}
            evidence_results.append(
                SearchEvidence(
                    rank=len(evidence_results) + 1,
                    score=result.score,
                    record_id=result.record_id,
                    chunk_id=metadata.get('chunk_id'),
                    asset_id=metadata.get('asset_id'),
                    project_id=metadata.get('project_id'),
                    chunk_order=metadata.get('chunk_order'),
                    text=result.text if include_text else None,
                    metadata=metadata if include_metadata else {},
                )
            )

        if not evidence_results:
            return int(HTTPStatus.OK), {
                'signal': ResponseSignal.SEMANTIC_SEARCH_NO_RESULTS.value,
                'message': 'Semantic search completed with no results.',
                'project_id': project_id,
                'query': search_request.query,
                'collection_name': collection_name,
                'embedding_model': actual_embedding_model,
                'total_results': 0,
                'results': [],
            }

        return int(HTTPStatus.OK), {
            'signal': ResponseSignal.SEMANTIC_SEARCH_SUCCESS.value,
            'message': 'Semantic search completed.',
            'project_id': project_id,
            'query': search_request.query,
            'collection_name': collection_name,
            'embedding_model': actual_embedding_model,
            'total_results': len(evidence_results),
            'results': [evidence.model_dump() for evidence in evidence_results],
        }
