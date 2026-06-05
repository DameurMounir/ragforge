from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    Boolean,
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
    from src.ragforge.stores.postgres.models.asset import AssetTable
    from src.ragforge.stores.postgres.models.project import ProjectTable


class DataChunkTable(TimestampMixin, Base):
    """
    Relational representation of an extracted document chunk.

    Branch 20 stores chunk text and metadata in PostgreSQL. Vector storage stays
    in Qdrant for the current RAG Core. Future branches may add PgVector-backed
    vector columns or a dedicated vector table.
    """

    __tablename__ = 'data_chunks'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chunk_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        server_default=text('gen_random_uuid()'),
        nullable=False,
    )

    project_pk: Mapped[int] = mapped_column(
        ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False,
    )
    asset_pk: Mapped[int] = mapped_column(
        ForeignKey('assets.id', ondelete='CASCADE'),
        nullable=False,
    )

    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_order: Mapped[int] = mapped_column(Integer, nullable=False)
    text_hash: Mapped[str | None] = mapped_column(String(length=64), nullable=True)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    char_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    char_end: Mapped[int | None] = mapped_column(Integer, nullable=True)

    chunk_metadata: Mapped[dict[str, Any]] = mapped_column(
        'metadata',
        JSONB,
        default=dict,
        server_default=text("'{}'::jsonb"),
        nullable=False,
    )

    embedded: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text('false'),
        nullable=False,
    )
    embedding_model: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    indexed_in_vector_store: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text('false'),
        nullable=False,
    )
    vector_record_id: Mapped[str | None] = mapped_column(String(length=255), nullable=True)

    project: Mapped['ProjectTable'] = relationship(back_populates='chunks')
    asset: Mapped['AssetTable'] = relationship(back_populates='chunks')

    __table_args__ = (
        UniqueConstraint('chunk_uuid', name='uq_data_chunks_chunk_uuid'),
        UniqueConstraint('asset_pk', 'chunk_order', name='uq_data_chunks_asset_order'),
        CheckConstraint('chunk_order >= 0', name='chunk_order_non_negative'),
        CheckConstraint('page_number IS NULL OR page_number >= 0', name='page_number_non_negative'),
        CheckConstraint('char_start IS NULL OR char_start >= 0', name='char_start_non_negative'),
        CheckConstraint('char_end IS NULL OR char_end >= 0', name='char_end_non_negative'),
        CheckConstraint('char_end IS NULL OR char_start IS NULL OR char_end >= char_start', name='valid_char_range'),
        CheckConstraint("char_length(btrim(chunk_text)) > 0", name='text_not_blank'),
        CheckConstraint("embedded = false OR embedding_model IS NOT NULL", name='embedded_requires_model'),
        CheckConstraint("indexed_in_vector_store = false OR vector_record_id IS NOT NULL", name='indexed_requires_vector_record'),
        Index('ix_chunks_project_pk', 'project_pk'),
        Index('ix_chunks_asset_pk', 'asset_pk'),
        Index('ix_chunks_project_asset_order', 'project_pk', 'asset_pk', 'chunk_order'),
        Index('ix_chunks_embedded', 'embedded'),
        Index('ix_chunks_vector_indexed', 'indexed_in_vector_store'),
        Index('ix_chunks_text_hash', 'text_hash'),
        Index(
            'uq_chunks_vector_record_id',
            'vector_record_id',
            unique=True,
            postgresql_where=text('vector_record_id IS NOT NULL'),
        ),
        Index('ix_chunks_metadata_gin', 'metadata', postgresql_using='gin'),
    )
