import pytest
from pydantic import ValidationError

from src.ragforge.schemas.answers import RAGAnswerRequest


def test_valid_rag_answer_request():
    request = RAGAnswerRequest(
        question='What is RAGForge?',
        limit=5,
        include_sources=True,
        include_evidence=True,
    )

    assert request.question == 'What is RAGForge?'
    assert request.limit == 5
    assert request.include_sources is True
    assert request.include_evidence is True


def test_question_is_stripped():
    request = RAGAnswerRequest(question='   What is indexing?   ')

    assert request.question == 'What is indexing?'


def test_empty_question_is_rejected():
    with pytest.raises(ValidationError):
        RAGAnswerRequest(question='   ')


def test_limit_must_be_positive():
    with pytest.raises(ValidationError):
        RAGAnswerRequest(
            question='Valid question',
            limit=0,
        )


def test_invalid_min_score_is_rejected():
    with pytest.raises(ValidationError):
        RAGAnswerRequest(
            question='Valid question',
            min_score=1.5,
        )
