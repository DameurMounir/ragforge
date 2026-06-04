from pydantic import BaseModel, Field, field_validator


class SemanticSearchRequest(BaseModel):
    """
    Request schema for Branch 17 semantic search.

    This schema represents the user query before answer generation.
    Branch 17 returns ranked evidence chunks only; it does not call the LLM
    to generate a final answer.
    """

    query: str = Field(..., min_length=1)
    limit: int | None = Field(default=None, gt=0)
    asset_id: str | None = None
    min_score: float | None = None
    include_text: bool | None = None
    include_metadata: bool | None = None

    @field_validator('query')
    @classmethod
    def validate_query(cls, value: str) -> str:
        """
        Normalize and validate the query.

        We strip whitespace here so the service always receives a clean query.
        """
        cleaned = value.strip()

        if not cleaned:
            raise ValueError('Search query must not be empty.')

        return cleaned

    @field_validator('min_score')
    @classmethod
    def validate_min_score(cls, value: float | None) -> float | None:
        """
        Validate optional score threshold.

        Qdrant cosine scores are usually between 0 and 1 in our current setup.
        Keeping this range explicit makes the API predictable.
        """
        if value is None:
            return value

        if value < 0 or value > 1:
            raise ValueError('min_score must be between 0 and 1.')

        return value


class SearchEvidence(BaseModel):
    """
    One ranked evidence chunk returned by semantic search.

    This object is intentionally source-rich because Branch 18 will use these
    evidence items to generate grounded answers with citations.
    """

    rank: int
    score: float
    record_id: str
    chunk_id: str | None = None
    asset_id: str | None = None
    project_id: str | None = None
    chunk_order: int | None = None
    text: str | None = None
    metadata: dict = Field(default_factory=dict)


class SemanticSearchResponse(BaseModel):
    """
    Structured response for semantic search.

    The response contains evidence only, not an LLM-generated answer.
    """

    signal: str
    message: str
    project_id: str
    query: str
    collection_name: str
    embedding_model: str
    total_results: int
    results: list[SearchEvidence]
