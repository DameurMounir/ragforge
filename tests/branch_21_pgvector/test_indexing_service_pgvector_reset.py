from types import SimpleNamespace

import pytest

from src.ragforge.models.enums.response_signals import ResponseSignal
from src.ragforge.schemas.indexing import IndexingRequest
from src.ragforge.services import indexing_service as service_module
from src.ragforge.services.indexing_service import IndexingService


class FakeSettings:
    EMBEDDING_MODEL = 'fake-embedding-model'
    EMBEDDING_PROVIDER = 'fake'
    EMBEDDING_VECTOR_SIZE = 3
    VECTOR_DB_DISTANCE = 'cosine'
    VECTOR_DB_COLLECTION_NAME = 'ragforge_chunks'


class FakeEmbeddingProvider:
    def embed_texts(self, embedding_request):
        return SimpleNamespace(
            embeddings=[[0.1, 0.2, 0.3] for _ in embedding_request.texts],
            model='fake-embedding-model',
        )


class FakeVectorDBService:
    created_instances = []

    def __init__(self, settings):
        self.settings = settings
        self.connected = False
        self.ensure_collection_calls = []
        self.delete_records_calls = []
        self.insert_many_calls = []
        FakeVectorDBService.created_instances.append(self)

    async def connect(self):
        self.connected = True

    async def close(self):
        self.connected = False

    async def ensure_collection(self, collection_name, vector_size, distance, do_reset=False):
        self.ensure_collection_calls.append(
            {
                'collection_name': collection_name,
                'vector_size': vector_size,
                'distance': distance,
                'do_reset': do_reset,
            }
        )
        return True

    async def delete_records(self, collection_name, filters=None):
        self.delete_records_calls.append(
            {
                'collection_name': collection_name,
                'filters': filters,
            }
        )
        return 2

    async def insert_many(self, collection_name, records, batch_size=64):
        self.insert_many_calls.append(
            {
                'collection_name': collection_name,
                'records': records,
                'batch_size': batch_size,
            }
        )
        return len(records)


class ProjectStoreFound:
    async def get_project_by_project_id(self, project_id: str):
        return SimpleNamespace(id='project-db-id')


class ProjectStoreNotFound:
    async def get_project_by_project_id(self, project_id: str):
        return None


class ChunkStoreWithChunks:
    def __init__(self):
        self.marked = []
        self.last_query = None

    async def get_project_chunks(
        self,
        project_id,
        asset_id=None,
        only_not_embedded=False,
        limit=None,
    ):
        self.last_query = {
            'project_id': project_id,
            'asset_id': asset_id,
            'only_not_embedded': only_not_embedded,
            'limit': limit,
        }
        return [
            SimpleNamespace(
                id='chunk-001',
                chunk_text='First chunk text for Branch 21.',
                chunk_metadata={
                    'project_id': 'malicious-or-stale-project-id',
                    'custom_key': 'custom-value',
                },
                chunk_project_id='project-db-id',
                chunk_asset_id='asset-db-id',
                chunk_order=1,
            )
        ]

    async def mark_chunks_embedded(self, indexed_chunks):
        self.marked.extend(indexed_chunks)
        return len(indexed_chunks)


class EmptyChunkStore:
    async def get_project_chunks(self, *args, **kwargs):
        return []


@pytest.fixture(autouse=True)
def patch_indexing_dependencies(monkeypatch):
    FakeVectorDBService.created_instances = []
    monkeypatch.setattr(
        service_module.EmbeddingProviderFactory,
        'create_provider',
        lambda settings: FakeEmbeddingProvider(),
    )
    monkeypatch.setattr(service_module, 'VectorDBService', FakeVectorDBService)


@pytest.mark.anyio
async def test_project_not_found_returns_404():
    service = IndexingService(settings=FakeSettings())
    status_code, response = await service.index_project_chunks(
        project_id='missing-project',
        indexing_request=IndexingRequest(),
        project_store=ProjectStoreNotFound(),
        chunk_store=EmptyChunkStore(),
    )
    assert status_code == 404
    assert response['signal'] == ResponseSignal.PROJECT_NOT_FOUND.value


@pytest.mark.anyio
async def test_do_reset_deletes_pgvector_records_for_project_and_asset():
    chunk_store = ChunkStoreWithChunks()
    service = IndexingService(settings=FakeSettings())

    status_code, response = await service.index_project_chunks(
        project_id='project21test',
        indexing_request=IndexingRequest(
            do_reset=True,
            asset_id='asset-db-id',
            batch_size=1,
            include_results=True,
        ),
        project_store=ProjectStoreFound(),
        chunk_store=chunk_store,
    )

    vector_service = FakeVectorDBService.created_instances[-1]
    assert status_code == 200
    assert response['signal'] == ResponseSignal.INDEXING_SUCCESS.value
    assert vector_service.ensure_collection_calls[0]['do_reset'] is False
    assert vector_service.delete_records_calls == [
        {
            'collection_name': 'ragforge_chunks',
            'filters': {
                'project_id': 'project-db-id',
                'asset_id': 'asset-db-id',
            },
        }
    ]
    assert len(vector_service.insert_many_calls[0]['records']) == 1
    inserted_record = vector_service.insert_many_calls[0]['records'][0]
    assert inserted_record.metadata['project_id'] == 'project-db-id'
    assert inserted_record.metadata['asset_id'] == 'asset-db-id'
    assert inserted_record.metadata['custom_key'] == 'custom-value'
    assert chunk_store.marked[0]['vector_id'] == 'chunk-001'


@pytest.mark.anyio
async def test_no_chunks_to_index_returns_bad_request():
    service = IndexingService(settings=FakeSettings())
    status_code, response = await service.index_project_chunks(
        project_id='project21test',
        indexing_request=IndexingRequest(),
        project_store=ProjectStoreFound(),
        chunk_store=EmptyChunkStore(),
    )
    assert status_code == 400
    assert response['signal'] == ResponseSignal.NO_CHUNKS_TO_INDEX.value
