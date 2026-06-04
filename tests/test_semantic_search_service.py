from types import SimpleNamespace

import pytest

from src.ragforge.models.enums.response_signals import ResponseSignal
from src.ragforge.schemas.search import SemanticSearchRequest
from src.ragforge.services import semantic_search_service as service_module
from src.ragforge.services.semantic_search_service import SemanticSearchService


class FakeSettings:
    """
    Explicit test settings.

    Tests should not rely on hidden defaults inside factories or services.
    """

    EMBEDDING_MODEL = 'text-embedding-3-small'
    VECTOR_DB_COLLECTION_NAME = 'ragforge_chunks'

    SEARCH_DEFAULT_LIMIT = 5
    SEARCH_MAX_LIMIT = 20
    SEARCH_MIN_SCORE = None
    SEARCH_INCLUDE_TEXT_DEFAULT = True
    SEARCH_INCLUDE_METADATA_DEFAULT = True


class FakeEmbeddingProvider:
    def embed_texts(self, embedding_request):
        return SimpleNamespace(
            embeddings=[[0.1, 0.2, 0.3]],
            model='fake-embedding-model',
        )


class FakeVectorDBService:
    """
    Fake vector DB service used to test the semantic search service without
    connecting to Qdrant.
    """

    results = []

    def __init__(self, settings):
        self.settings = settings
        self.connected = False

    def connect(self):
        self.connected = True

    def close(self):
        self.connected = False

    def search_by_vector(self, collection_name, vector, limit, filters):
        return self.results


class ProjectStoreNotFound:
    async def get_project_by_project_id(self, project_id: str):
        return None


class ProjectStoreFound:
    async def get_project_by_project_id(self, project_id: str):
        return SimpleNamespace(id='mongo-project-object-id')


@pytest.fixture(autouse=True)
def patch_service_dependencies(monkeypatch):
    """
    Patch factories/services at the module boundary.

    This keeps the unit tests focused on service orchestration, not on Qdrant
    or real embedding providers.
    """

    monkeypatch.setattr(
        service_module.EmbeddingProviderFactory,
        'create_provider',
        lambda settings: FakeEmbeddingProvider(),
    )
    monkeypatch.setattr(
        service_module,
        'VectorDBService',
        FakeVectorDBService,
    )


@pytest.mark.anyio
async def test_project_not_found_returns_not_found():
    service = SemanticSearchService(settings=FakeSettings())

    status_code, response = await service.search_project_chunks(
        project_id='missing-project',
        search_request=SemanticSearchRequest(query='test query'),
        project_store=ProjectStoreNotFound(),
    )

    assert status_code == 404
    assert response['signal'] == ResponseSignal.PROJECT_NOT_FOUND.value


@pytest.mark.anyio
async def test_search_no_results():
    FakeVectorDBService.results = []
    service = SemanticSearchService(settings=FakeSettings())

    status_code, response = await service.search_project_chunks(
        project_id='project16test',
        search_request=SemanticSearchRequest(query='test query'),
        project_store=ProjectStoreFound(),
    )

    assert status_code == 200
    assert response['signal'] == ResponseSignal.SEMANTIC_SEARCH_NO_RESULTS.value
    assert response['total_results'] == 0


@pytest.mark.anyio
async def test_search_success_maps_ranked_evidence():
    FakeVectorDBService.results = [
        SimpleNamespace(
            record_id='chunk-vector-id',
            score=0.91,
            text='RAGForge semantic search evidence text.',
            metadata={
                'chunk_id': 'chunk-id',
                'asset_id': 'asset-id',
                'project_id': 'mongo-project-object-id',
                'chunk_order': 1,
            },
        )
    ]

    service = SemanticSearchService(settings=FakeSettings())

    status_code, response = await service.search_project_chunks(
        project_id='project16test',
        search_request=SemanticSearchRequest(query='semantic search'),
        project_store=ProjectStoreFound(),
    )

    assert status_code == 200
    assert response['signal'] == ResponseSignal.SEMANTIC_SEARCH_SUCCESS.value
    assert response['total_results'] == 1
    assert response['results'][0]['rank'] == 1
    assert response['results'][0]['record_id'] == 'chunk-vector-id'
    assert response['results'][0]['chunk_id'] == 'chunk-id'


@pytest.mark.anyio
async def test_include_text_and_metadata_flags_hide_optional_fields():
    FakeVectorDBService.results = [
        SimpleNamespace(
            record_id='chunk-vector-id',
            score=0.91,
            text='This text should be hidden.',
            metadata={
                'chunk_id': 'chunk-id',
                'asset_id': 'asset-id',
            },
        )
    ]

    service = SemanticSearchService(settings=FakeSettings())

    status_code, response = await service.search_project_chunks(
        project_id='project16test',
        search_request=SemanticSearchRequest(
            query='semantic search',
            include_text=False,
            include_metadata=False,
        ),
        project_store=ProjectStoreFound(),
    )

    assert status_code == 200
    assert response['results'][0]['text'] is None
    assert response['results'][0]['metadata'] == {}
