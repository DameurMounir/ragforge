from typing import Any

from pydantic import BaseModel, Field


class VectorRecord(BaseModel):
    """
    One vector record to insert into the vector database.
    """

    record_id: str | int | None = None
    vector: list[float]
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class VectorSearchResult(BaseModel):
    """
    Normalized vector search result returned by any vector DB provider.
    """

    record_id: str | int | None = None
    score: float | None = None
    text: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)