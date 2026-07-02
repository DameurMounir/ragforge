from typing import Any, Literal, Self

from pydantic import BaseModel, Field, model_validator


class ProcessDocumentRequest(BaseModel):
    """Request body for one document or all project documents."""

    asset_id: str | None = Field(default=None, min_length=1)
    stored_filename: str | None = Field(default=None, min_length=1)
    chunk_size: int = Field(default=1000, gt=0)
    overlap_size: int = Field(default=200, ge=0)
    do_reset: bool = False
    include_chunks: bool = False

    @model_validator(mode="after")
    def validate_processing_request(self) -> Self:
        if self.asset_id and self.stored_filename:
            raise ValueError("Use either asset_id or stored_filename, not both.")
        if self.overlap_size >= self.chunk_size:
            raise ValueError("overlap_size must be smaller than chunk_size")
        return self


class ProcessedAssetResponse(BaseModel):
    asset_id: str
    asset_name: str
    file_name: str | None = None
    status: str
    inserted_chunks: int = Field(ge=0)
    chunks: list[dict[str, Any]] | None = None


class FailedAssetResponse(BaseModel):
    asset_id: str
    asset_name: str
    status: str
    error: str


class SkippedAssetResponse(BaseModel):
    asset_id: str | None
    asset_name: str
    reason: str


class ProcessDocumentResponse(BaseModel):
    signal: str
    message: str
    project_id: str
    mode: Literal[
        "single_asset_by_id",
        "single_asset_by_filename",
        "all_project_file_assets",
    ]
    chunk_size: int = Field(gt=0)
    overlap_size: int = Field(ge=0)
    do_reset: bool
    processed_files: int = Field(ge=0)
    failed_files: int = Field(ge=0)
    skipped_files: int = Field(ge=0)
    inserted_chunks: int = Field(ge=0)
    deleted_chunks: int = Field(ge=0)
    processed_assets: list[ProcessedAssetResponse] = Field(default_factory=list)
    failed_assets: list[FailedAssetResponse] = Field(default_factory=list)
    skipped_assets: list[SkippedAssetResponse] = Field(default_factory=list)
