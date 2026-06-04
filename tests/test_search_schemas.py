import pytest
from pydantic import ValidationError

from src.ragforge.schemas.search import SemanticSearchRequest


def test_valid_semantic_search_request():
    request = SemanticSearchRequest(
        query='What is semantic search?',
        limit=5,
        include_text=True,
        include_metadata=True,
    )

    assert request.query == 'What is semantic search?'
    assert request.limit == 5
    assert request.include_text is True
    assert request.include_metadata is True


def test_query_is_stripped():
    request = SemanticSearchRequest(query='   semantic search   ')

    assert request.query == 'semantic search'


def test_empty_query_is_rejected():
    with pytest.raises(ValidationError):
        SemanticSearchRequest(query='   ')


def test_limit_must_be_positive():
    with pytest.raises(ValidationError):
        SemanticSearchRequest(
            query='valid query',
            limit=0,
        )


def test_invalid_min_score_is_rejected():
    with pytest.raises(ValidationError):
        SemanticSearchRequest(
            query='valid query',
            min_score=1.5,
        )
