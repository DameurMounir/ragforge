from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.ragforge.stores.postgres.models.base import Base
from src.ragforge.stores.postgres.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from src.ragforge.stores.postgres.models.data_chunk import DataChunkTable
    from src.ragforge.stores.postgres.models.project import ProjectTable


class AssetTable(TimestampMixin, Base):
    """
    Relational representation of an uploaded or registered RAGForge asset.

    Important identity rule:
    - `asset_name` and `original_filename` are human-facing names and may repeat.
    - `stored_filename` and `storage_path` are technical identifiers and are unique
      inside a project when present.
    """

    __tablename__ = 'assets'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asset_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        server_default=text('gen_random_uuid()'),
        nullable=False,
    )

    project_pk: Mapped[int] = mapped_column(
        ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False,
    )

    asset_type: Mapped[str] = mapped_column(String(length=50), nullable=False)
    asset_name: Mapped[str] = mapped_column(String(length=512), nullable=False)
    original_filename: Mapped[str | None] = mapped_column(String(length=512), nullable=True)
    stored_filename: Mapped[str | None] = mapped_column(String(length=512), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    storage_path: Mapped[str | None] = mapped_column(String(length=1024), nullable=True)

    asset_status: Mapped[str] = mapped_column(
        String(length=50),
        default='uploaded',
        server_default=text("'uploaded'"),
        nullable=False,
    )
    chunk_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text('0'),
        nullable=False,
    )
    extraction_method: Mapped[str | None] = mapped_column(String(length=100), nullable=True)
    extraction_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    asset_metadata: Mapped[dict[str, Any]] = mapped_column(
        'metadata',
        JSONB,
        default=dict,
        server_default=text("'{}'::jsonb"),
        nullable=False,
    )

    project: Mapped['ProjectTable'] = relationship(back_populates='assets')
    chunks: Mapped[list['DataChunkTable']] = relationship(
        back_populates='asset',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    __table_args__ = (
        UniqueConstraint('asset_uuid', name='uq_assets_asset_uuid'),
        CheckConstraint('chunk_count >= 0', name='chunk_count_non_negative'),
        CheckConstraint('size_bytes IS NULL OR size_bytes >= 0', name='size_bytes_non_negative'),
        Index('ix_assets_project_pk', 'project_pk'),
        Index('ix_assets_project_type', 'project_pk', 'asset_type'),
        Index('ix_assets_project_status', 'project_pk', 'asset_status'),
        # Partial unique indexes allow non-file assets with NULL stored path values,
        # while protecting uploaded files from duplicate technical identifiers.
        Index(
            'uq_assets_project_stored_filename',
            'project_pk',
            'stored_filename',
            unique=True,
            postgresql_where=text('stored_filename IS NOT NULL'),
        ),
        Index(
            'uq_assets_project_storage_path',
            'project_pk',
            'storage_path',
            unique=True,
            postgresql_where=text('storage_path IS NOT NULL'),
        ),
        # General JSONB index for metadata filtering. Future branches can replace
        # or complement it with expression indexes when query patterns stabilize.
        Index('ix_assets_metadata_gin', 'metadata', postgresql_using='gin'),
    )
