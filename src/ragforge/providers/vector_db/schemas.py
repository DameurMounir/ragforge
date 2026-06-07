from typing import Any

from pydantic import BaseModel, Field, field_validator


class VectorRecord(BaseModel):
    """One vector record to insert into the vector database."""

    record_id: str | int | None = None
    vector: list[float]
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator('vector')
    @classmethod
    def validate_vector(cls, value: list[float]) -> list[float]:
        if not value:
            raise ValueError('Vector must not be empty.')
        return [float(item) for item in value]

    @field_validator('text')
    @classmethod
    def validate_text(cls, value: str) -> str:
        if not str(value).strip():
            raise ValueError('Vector record text must not be empty.')
        return value


class VectorSearchResult(BaseModel):
    """Normalized vector search result returned by any vector DB provider."""

    record_id: str | int | None = None
    score: float | None = None
    text: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
