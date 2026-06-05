from __future__ import annotations

from src.ragforge.stores.postgres.models.asset import AssetTable
from src.ragforge.stores.postgres.models.data_chunk import DataChunkTable
from src.ragforge.stores.postgres.models.project import ProjectTable
from src.ragforge.stores.postgres.records import (
    AssetRecord,
    DataChunkRecord,
    ProjectRecord,
)


def project_to_record(row: ProjectTable) -> ProjectRecord:
    """Convert a SQLAlchemy ProjectTable row into a backend-neutral record."""

    return ProjectRecord(
        pk=row.id,
        project_uuid=row.project_uuid,
        project_id=row.project_id,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def asset_to_record(row: AssetTable) -> AssetRecord:
    """Convert a SQLAlchemy AssetTable row into a backend-neutral record."""

    return AssetRecord(
        pk=row.id,
        asset_uuid=row.asset_uuid,
        project_pk=row.project_pk,
        asset_type=row.asset_type,
        asset_name=row.asset_name,
        original_filename=row.original_filename,
        stored_filename=row.stored_filename,
        mime_type=row.mime_type,
        size_bytes=row.size_bytes,
        storage_path=row.storage_path,
        asset_status=row.asset_status,
        chunk_count=row.chunk_count,
        extraction_method=row.extraction_method,
        extraction_error=row.extraction_error,
        asset_metadata=dict(row.asset_metadata or {}),
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def chunk_to_record(row: DataChunkTable) -> DataChunkRecord:
    """Convert a SQLAlchemy DataChunkTable row into a backend-neutral record."""

    return DataChunkRecord(
        pk=row.id,
        chunk_uuid=row.chunk_uuid,
        project_pk=row.project_pk,
        asset_pk=row.asset_pk,
        chunk_text=row.chunk_text,
        chunk_order=row.chunk_order,
        text_hash=row.text_hash,
        page_number=row.page_number,
        char_start=row.char_start,
        char_end=row.char_end,
        chunk_metadata=dict(row.chunk_metadata or {}),
        embedded=row.embedded,
        embedding_model=row.embedding_model,
        indexed_in_vector_store=row.indexed_in_vector_store,
        vector_record_id=row.vector_record_id,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )
