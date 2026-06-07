from types import SimpleNamespace

import pytest

from src.ragforge.models.enums.response_signals import ResponseSignal
from src.ragforge.schemas.search import SemanticSearchRequest
from src.ragforge.services import semantic_search_service as service_module
from src.ragforge.services.semantic_search_service import SemanticSearchService


class FakeSettings:
    EMBEDDING_MODEL = 'fake-embedding-model'
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
    results = []
    created_instances = []

    def __init__(self, settings):
        self.settings = settings
        self.connected = False
        self.search_calls = []
        FakeVectorDBService.created_instances.append(self)

    async def connect(self):
        self.connected = True

    async def close(self):
        self.connected = False

    async def search_by_vector(self, collection_name, vector, limit, filters):
        self.search_calls.append(
            {
                'collection_name': collection_name,
                'vector': vector,
                'limit': limit,
                'filters': filters,
            }
        )
        return self.results


class ProjectStoreNotFound:
    async def get_project_by_project_id(self, project_id: str):
        return None


class ProjectStoreFound:
    async def get_project_by_project_id(self, project_id: str):
        return SimpleNamespace(id='project-db-id')


@pytest.fixture(autouse=True)
def patch_service_dependencies(monkeypatch):
    FakeVectorDBService.results = []
    FakeVectorDBService.created_instances = []
    monkeypatch.setattr(
        service_module.EmbeddingProviderFactory,
        'create_provider',
        lambda settings: FakeEmbeddingProvider(),
    )
    monkeypatch.setattr(service_module, 'VectorDBService', FakeVectorDBService)


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
    service = SemanticSearchService(settings=FakeSettings())
    status_code, response = await service.search_project_chunks(
        project_id='project21test',
        search_request=SemanticSearchRequest(query='test query'),
        project_store=ProjectStoreFound(),
    )
    assert status_code == 200
    assert response['signal'] == ResponseSignal.SEMANTIC_SEARCH_NO_RESULTS.value
    assert response['total_results'] == 0


@pytest.mark.anyio
async def test_search_success_maps_ranked_evidence_and_filters_project():
    FakeVectorDBService.results = [
        SimpleNamespace(
            record_id='chunk-vector-id',
            score=0.91,
            text='RAGForge semantic search evidence text.',
            metadata={
                'chunk_id': 'chunk-id',
                'asset_id': 'asset-id',
                'project_id': 'project-db-id',
                'chunk_order': 1,
            },
        )
    ]
    service = SemanticSearchService(settings=FakeSettings())
    status_code, response = await service.search_project_chunks(
        project_id='project21test',
        search_request=SemanticSearchRequest(query='semantic search'),
        project_store=ProjectStoreFound(),
    )
    vector_service = FakeVectorDBService.created_instances[-1]
    assert status_code == 200
    assert response['signal'] == ResponseSignal.SEMANTIC_SEARCH_SUCCESS.value
    assert response['total_results'] == 1
    assert response['results'][0]['rank'] == 1
    assert response['results'][0]['record_id'] == 'chunk-vector-id'
    assert response['results'][0]['chunk_id'] == 'chunk-id'
    assert vector_service.search_calls[0]['filters'] == {'project_id': 'project-db-id'}


@pytest.mark.anyio
async def test_asset_filter_is_passed_to_vector_backend():
    service = SemanticSearchService(settings=FakeSettings())
    await service.search_project_chunks(
        project_id='project21test',
        search_request=SemanticSearchRequest(
            query='semantic search',
            asset_id='asset-id',
        ),
        project_store=ProjectStoreFound(),
    )
    vector_service = FakeVectorDBService.created_instances[-1]
    assert vector_service.search_calls[0]['filters'] == {
        'project_id': 'project-db-id',
        'asset_id': 'asset-id',
    }


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
        project_id='project21test',
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
