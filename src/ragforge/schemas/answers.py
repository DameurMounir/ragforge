from pydantic import BaseModel, Field, field_validator


class RAGAnswerRequest(BaseModel):
    """
    Request schema for Branch 18 augmented answers.

    Branch 18 consumes Branch 17 semantic search evidence and generates
    a grounded answer with sources.
    """

    question: str = Field(..., min_length=1)
    limit: int | None = Field(default=None, gt=0)
    asset_id: str | None = None
    min_score: float | None = None
    include_sources: bool | None = None
    include_evidence: bool | None = None
    include_debug_prompt: bool | None = None

    @field_validator('question')
    @classmethod
    def validate_question(cls, value: str) -> str:
        """
        Normalize and validate the question.
        """
        cleaned = value.strip()

        if not cleaned:
            raise ValueError('Question must not be empty.')

        return cleaned

    @field_validator('min_score')
    @classmethod
    def validate_min_score(cls, value: float | None) -> float | None:
        """
        Validate optional score threshold.

        The current semantic search API keeps score thresholds predictable
        by accepting values between 0 and 1.
        """
        if value is None:
            return value

        if value < 0 or value > 1:
            raise ValueError('min_score must be between 0 and 1.')

        return value


class AnswerSource(BaseModel):
    """
    Source metadata used by the generated answer.

    Sources are intentionally separate from evidence text so the API can
    return citations without always returning full chunk text.
    """

    source_number: int
    rank: int
    score: float
    record_id: str
    chunk_id: str | None = None
    asset_id: str | None = None
    project_id: str | None = None
    chunk_order: int | None = None
    metadata: dict = Field(default_factory=dict)


class AnswerEvidence(BaseModel):
    """
    Evidence text used to build the answer context.
    """

    source_number: int
    text: str
    score: float
    chunk_id: str | None = None
    asset_id: str | None = None
    chunk_order: int | None = None
    metadata: dict = Field(default_factory=dict)


class RAGAnswerResponse(BaseModel):
    """
    Structured response for grounded RAG answers.
    """

    signal: str
    message: str
    project_id: str
    question: str
    answer: str | None = None
    sources: list[AnswerSource] = Field(default_factory=list)
    evidence: list[AnswerEvidence] = Field(default_factory=list)
    llm_model: str | None = None
    retrieval_count: int = 0
    debug_prompt: str | None = None
