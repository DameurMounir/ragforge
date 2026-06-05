from types import SimpleNamespace

import pytest

from src.ragforge.models.enums.response_signals import ResponseSignal
from src.ragforge.schemas.answers import RAGAnswerRequest
from src.ragforge.services import rag_answer_service as service_module
from src.ragforge.services.rag_answer_service import RAGAnswerService


class FakeSettings:
    RAG_ANSWER_DEFAULT_LIMIT = 5
    RAG_ANSWER_MAX_CONTEXT_CHARS = 4000
    RAG_ANSWER_INCLUDE_SOURCES_DEFAULT = True
    RAG_ANSWER_INCLUDE_EVIDENCE_DEFAULT = True
    RAG_ANSWER_DEBUG_PROMPT_DEFAULT = False

    SEARCH_MAX_LIMIT = 20

    RAG_ENABLE_CITATION_VALIDATION = True
    RAG_RETRIEVAL_CANDIDATE_LIMIT = 10
    RAG_RETRIEVAL_MIN_SCORE = None
    RAG_MAX_CHUNKS_PER_ASSET = 3
    RAG_ENABLE_SOURCE_DEDUP = True
    RAG_ENABLE_DOMINANT_ASSET = True
    RAG_DOMINANT_ASSET_SCORE_GAP = 0.05
    RAG_DOMINANT_ASSET_MIN_CHUNKS = 2

    LLM_PROVIDER = 'fake'
    LLM_DEFAULT_MODEL = 'fake-ragforge-model'
    LLM_TEMPERATURE = 0.2
    LLM_MAX_OUTPUT_TOKENS = 512


class FakeSemanticSearchServiceSuccess:
    def __init__(self, settings):
        self.settings = settings

    async def search_project_chunks(
        self,
        project_id,
        search_request,
        project_store,
    ):
        return 200, {
            'signal': 'semantic_search_success',
            'message': 'Semantic search completed.',
            'project_id': project_id,
            'query': search_request.query,
            'collection_name': 'ragforge_chunks',
            'embedding_model': 'fake-embedding-model',
            'total_results': 1,
            'results': [
                {
                    'rank': 1,
                    'score': 0.91,
                    'record_id': 'record-1',
                    'chunk_id': 'chunk-1',
                    'asset_id': 'asset-1',
                    'project_id': 'mongo-project-id',
                    'chunk_order': 1,
                    'text': 'RAGForge indexes chunks into Qdrant.',
                    'metadata': {'file_name': 'demo.txt'},
                }
            ],
        }


class FakeSemanticSearchServiceNoResults:
    def __init__(self, settings):
        self.settings = settings

    async def search_project_chunks(
        self,
        project_id,
        search_request,
        project_store,
    ):
        return 200, {
            'signal': 'semantic_search_no_results',
            'message': 'Semantic search completed with no results.',
            'project_id': project_id,
            'query': search_request.query,
            'collection_name': 'ragforge_chunks',
            'embedding_model': 'fake-embedding-model',
            'total_results': 0,
            'results': [],
        }


class FakeLLMService:
    def __init__(self, settings):
        self.settings = settings

    async def generate(self, request):
        return SimpleNamespace(
            content='RAGForge indexes chunks into a vector database.',
            model='fake-ragforge-model',
        )


@pytest.mark.anyio
async def test_answer_success_returns_sources(monkeypatch):
    monkeypatch.setattr(
        service_module,
        'SemanticSearchService',
        FakeSemanticSearchServiceSuccess,
    )
    monkeypatch.setattr(
        service_module,
        'LLMService',
        FakeLLMService,
    )

    service = RAGAnswerService(settings=FakeSettings())

    status_code, response = await service.answer_project_question(
        project_id='project18test',
        answer_request=RAGAnswerRequest(
            question='What does RAGForge index?',
        ),
        project_store=SimpleNamespace(),
    )

    assert status_code == 200
    assert response['signal'] == ResponseSignal.RAG_ANSWER_SUCCESS.value
    assert response['answer']
    assert response['sources']
    assert response['evidence']
    assert response['llm_model'] == 'fake-ragforge-model'


@pytest.mark.anyio
async def test_answer_no_context(monkeypatch):
    monkeypatch.setattr(
        service_module,
        'SemanticSearchService',
        FakeSemanticSearchServiceNoResults,
    )
    monkeypatch.setattr(
        service_module,
        'LLMService',
        FakeLLMService,
    )

    service = RAGAnswerService(settings=FakeSettings())

    status_code, response = await service.answer_project_question(
        project_id='project18test',
        answer_request=RAGAnswerRequest(
            question='Unknown question?',
        ),
        project_store=SimpleNamespace(),
    )

    assert status_code == 200
    assert response['signal'] == ResponseSignal.RAG_ANSWER_NO_CONTEXT.value
    assert response['sources'] == []
    assert response['evidence'] == []
