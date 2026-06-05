from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class ProjectRecord:
    """ORM-neutral project record returned by repositories."""

    pk: int
    project_uuid: UUID
    project_id: str
    created_at: datetime
    updated_at: datetime | None = None


@dataclass(frozen=True)
class AssetRecord:
    """ORM-neutral asset record returned by repositories."""

    pk: int
    asset_uuid: UUID
    project_pk: int
    asset_type: str
    asset_name: str
    original_filename: str | None = None
    stored_filename: str | None = None
    mime_type: str | None = None
    size_bytes: int | None = None
    storage_path: str | None = None
    asset_status: str = 'uploaded'
    chunk_count: int = 0
    extraction_method: str | None = None
    extraction_error: str | None = None
    asset_metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(frozen=True)
class DataChunkRecord:
    """ORM-neutral chunk record returned by repositories."""

    pk: int
    chunk_uuid: UUID
    project_pk: int
    asset_pk: int
    chunk_text: str
    chunk_order: int
    text_hash: str | None = None
    page_number: int | None = None
    char_start: int | None = None
    char_end: int | None = None
    chunk_metadata: dict[str, Any] = field(default_factory=dict)
    embedded: bool = False
    embedding_model: str | None = None
    indexed_in_vector_store: bool = False
    vector_record_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
