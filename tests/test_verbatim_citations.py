from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.ragforge.models.enums.response_signals import ResponseSignal
from src.ragforge.schemas.answers import RAGAnswerRequest
from src.ragforge.services import rag_answer_service as service_module
from src.ragforge.services.citation_validator import CitationValidator
from tests.test_rag_answer_service import FakeSemanticSearchServiceSuccess, FakeSettings


@pytest.mark.parametrize(
    ('passage', 'claim'),
    [
        ('Le délai est de 30 jours. Les recours prennent 90 jours.', 'Le délai est de 90 jours'),
        ('The process takes 30 hours.', 'The process takes 30 days'),
        ('تتطلب المراجعة ٣٠ يوماً.', 'تتطلب المراجعة ٩٠ يوماً'),
        ('The owner need not approve.', 'The owner must approve'),
        ('Le délai est de 30 jours si le dossier est complet.', 'Le délai est de 30 jours'),
    ],
)
def test_misquotation_is_withheld(passage, claim):
    result = CitationValidator().verify_excerpts(f'{claim} [Source 1].', {1: passage})

    assert result['review_required'] is True
    assert result['accepted_claims'] == 0
    assert result['answer'] == CitationValidator.ABSTENTION


@pytest.mark.parametrize(
    'passage',
    ['Le délai est de 30 jours.', 'The limit is 2.5 days.', 'مهلة المراجعة ٣٠ يوماً.'],
)
def test_exact_excerpt_retains_source_text_and_attribution(passage):
    result = CitationValidator().verify_excerpts(
        passage.removesuffix('.') + ' [Source 2].', {2: passage}
    )
    assert result['review_required'] is False
    assert result['answer'] == f'{passage} [Source 2]'


def test_each_claim_must_be_attributed_and_supported_by_all_its_sources():
    result = CitationValidator().verify_excerpts(
        'Approval is required. [Sources 1, 2]\n'
        'The delay is two days. [Sources 1, 2]\n'
        'Approval is optional.\n'
        'Approval is required. [Source 8]',
        {
            1: 'The delay is two days. Approval is required.',
            2: 'Approval is required.',
        },
    )
    assert result['review_required'] is True
    assert result['invalid_source_numbers'] == [8]
    assert result['accepted_claims'] == 1 and result['rejected_claims'] == 3
    assert result['answer'] == 'Approval is required. [Sources 1, 2]'


def test_wholly_invalid_reference_in_legacy_mode_withholds_claim():
    result = CitationValidator().validate_and_sanitize('The limit is 90 days [Source 7].', [1])
    assert result['review_required'] is True
    assert result['answer'] == CitationValidator.ABSTENTION


@pytest.mark.anyio
async def test_answer_service_enforces_requested_policy_even_when_legacy_validation_is_off(monkeypatch):
    monkeypatch.setattr(service_module, 'SemanticSearchService', FakeSemanticSearchServiceSuccess)
    llm = AsyncMock()
    llm.generate.return_value = SimpleNamespace(
        content='RAGForge indexes chunks into Qdrant. [Source 1]\nEverything is free. [Source 1]',
        model='test',
    )
    monkeypatch.setattr(service_module, 'LLMService', lambda **kwargs: llm)
    settings = FakeSettings()
    settings.RAG_ENABLE_CITATION_VALIDATION = False
    service = service_module.RAGAnswerService(settings=settings)
    code, response = await service.answer_project_question(
        'project',
        RAGAnswerRequest(question='Where?', citation_policy='verbatim', include_evidence=False),
        SimpleNamespace(),
    )
    assert code == 200
    assert response['signal'] == ResponseSignal.RAG_ANSWER_REVIEW_REQUIRED.value
    assert response['answer'] == 'RAGForge indexes chunks into Qdrant. [Source 1]'
    assert response['evidence'] == []
    assert response['warnings']
    assert response['citation_validation']['rejected_claims'] == 1
    assert 'complete sentences' in llm.generate.call_args.args[0].system_prompt
