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

    RAG_RETRIEVAL_CANDIDATE_LIMIT = 10
    RAG_RETRIEVAL_MIN_SCORE = 0.25
    RAG_MAX_CHUNKS_PER_ASSET = 3
    RAG_ENABLE_SOURCE_DEDUP = True
    RAG_ENABLE_DOMINANT_ASSET = True
    RAG_DOMINANT_ASSET_SCORE_GAP = 0.08
    RAG_DOMINANT_ASSET_MIN_CHUNKS = 2
    RAG_ENABLE_CITATION_VALIDATION = True

    SEARCH_MAX_LIMIT = 50

    LLM_PROVIDER = 'fake'
    LLM_DEFAULT_MODEL = 'fake-ragforge-model'
    LLM_TEMPERATURE = 0.2
    LLM_MAX_OUTPUT_TOKENS = 512


class FakeSemanticSearchServiceMixedEvidence:
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
            'embedding_model': 'text-embedding-3-small',
            'total_results': 4,
            'results': [
                {
                    'rank': 1,
                    'score': 0.63,
                    'record_id': 'record-1',
                    'chunk_id': 'chunk-1',
                    'asset_id': 'asset-td',
                    'project_id': 'mongo-project-id',
                    'chunk_order': 1,
                    'text': 'Encadré par : Pr. Hatim Derrouz.',
                    'metadata': {'source': 'TD1_Logique_IA.pdf'},
                },
                {
                    'rank': 2,
                    'score': 0.56,
                    'record_id': 'record-2',
                    'chunk_id': 'chunk-2',
                    'asset_id': 'asset-td',
                    'project_id': 'mongo-project-id',
                    'chunk_order': 2,
                    'text': 'Master Intelligence Artificielle et Cybersécurité.',
                    'metadata': {'source': 'TD1_Logique_IA.pdf'},
                },
                {
                    'rank': 3,
                    'score': 0.21,
                    'record_id': 'record-3',
                    'chunk_id': 'chunk-3',
                    'asset_id': 'asset-other',
                    'project_id': 'mongo-project-id',
                    'chunk_order': 1,
                    'text': 'A weak unrelated module chunk.',
                    'metadata': {'source': 'other.pdf'},
                },
            ],
        }


class FakeLLMServiceWithInvalidCitation:
    def __init__(self, settings):
        self.settings = settings

    async def generate(self, request):
        return SimpleNamespace(
            content='Le professeur est Pr. Hatim Derrouz [Sources 1, 13].',
            model='fake-ragforge-model',
        )


@pytest.mark.anyio
async def test_answer_service_filters_weak_chunks_and_sanitizes_citations(monkeypatch):
    monkeypatch.setattr(
        service_module,
        'SemanticSearchService',
        FakeSemanticSearchServiceMixedEvidence,
    )
    monkeypatch.setattr(
        service_module,
        'LLMService',
        FakeLLMServiceWithInvalidCitation,
    )

    service = RAGAnswerService(settings=FakeSettings())

    status_code, response = await service.answer_project_question(
        project_id='project19test',
        answer_request=RAGAnswerRequest(
            question='Quel est le nom du professeur ?',
        ),
        project_store=SimpleNamespace(),
    )

    assert status_code == 200
    assert response['signal'] == ResponseSignal.RAG_ANSWER_SUCCESS.value
    assert '13' not in response['answer']
    assert response['citation_validation']['invalid_source_numbers'] == [13]
    assert response['retrieval_diagnostics']['removed_below_min_score'] == 1
    assert response['retrieval_count'] == 2
    assert response['sources']
