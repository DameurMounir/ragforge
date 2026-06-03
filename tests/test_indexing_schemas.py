import pytest
from pydantic import ValidationError

from src.ragforge.providers.embedding.enums import (
    IndexingGranularity,
    IndexingStrategy,
)
from src.ragforge.schemas.indexing import IndexingRequest


def test_indexing_request_defaults_to_simple_chunk():
    request = IndexingRequest()

    assert request.strategy == IndexingStrategy.SIMPLE_CHUNK
    assert request.granularity == IndexingGranularity.CHUNK


def test_indexing_request_rejects_late_chunking_in_branch_16():
    with pytest.raises(ValidationError):
        IndexingRequest(strategy=IndexingStrategy.LATE_CHUNKING)


def test_indexing_request_rejects_asset_granularity_in_branch_16():
    with pytest.raises(ValidationError):
        IndexingRequest(granularity=IndexingGranularity.ASSET)
