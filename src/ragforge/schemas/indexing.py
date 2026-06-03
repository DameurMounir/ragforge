from pydantic import BaseModel, Field, model_validator

from src.ragforge.providers.embedding.enums import (
    IndexingGranularity,
    IndexingStrategy,
)


class IndexingRequest(BaseModel):
    """
    Request body for indexing MongoDB chunks into Qdrant.

    Branch 16 implements only SIMPLE_CHUNK.
    Other strategies are declared now to keep the architecture open for
    late chunking and hierarchical retrieval later.
    """

    asset_id: str | None = None
    do_reset: bool = False
    batch_size: int = Field(default=32, gt=0, le=256)
    limit: int | None = Field(default=None, gt=0)
    strategy: IndexingStrategy = IndexingStrategy.SIMPLE_CHUNK
    granularity: IndexingGranularity = IndexingGranularity.CHUNK
    include_results: bool = False

    @model_validator(mode='after')
    def validate_branch_16_scope(self):
        if self.strategy != IndexingStrategy.SIMPLE_CHUNK:
            raise ValueError(
                'Branch 16 only implements simple_chunk indexing. '
                'late_chunking, asset_summary, and hierarchical are reserved '
                'for future branches.'
            )

        if self.granularity != IndexingGranularity.CHUNK:
            raise ValueError(
                'Branch 16 only implements chunk granularity.'
            )

        return self


class IndexedChunkResult(BaseModel):
    chunk_id: str
    asset_id: str
    vector_id: str
    chunk_order: int
    embedding_model: str
    indexed: bool = True


class IndexingResponse(BaseModel):
    signal: str
    message: str
    project_id: str
    asset_id: str | None = None
    strategy: str
    granularity: str
    collection_name: str
    embedding_model: str
    indexed_chunks: int
    failed_chunks: int
    skipped_chunks: int
    results: list[IndexedChunkResult] = Field(default_factory=list)
