from __future__ import annotations

import uuid
from typing import Any

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import (
    CheckConstraint,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text as sql_text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.ragforge.stores.postgres.models.base import Base
from src.ragforge.stores.postgres.models.mixins import TimestampMixin


class VectorRecordTable(TimestampMixin, Base):
    """
    Alembic-managed PgVector storage table.

    The embedding column intentionally uses the variable-dimension `vector` type.
    The actual dimension is stored in vector_size and checked in PostgreSQL with
    vector_dims(embedding) = vector_size. This keeps Branch 21 configurable from
    environment settings without binding the project to one embedding model.
    """

    __tablename__ = 'vector_records'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vector_record_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        server_default=sql_text('gen_random_uuid()'),
        nullable=False,
        unique=True,
    )

    collection_name: Mapped[str] = mapped_column(String(length=150), nullable=False)
    record_id: Mapped[str] = mapped_column(String(length=255), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    embedding: Mapped[list[float]] = mapped_column(VECTOR(), nullable=False)
    vector_size: Mapped[int] = mapped_column(Integer, nullable=False)

    embedding_model: Mapped[str] = mapped_column(String(length=255), nullable=False)
    embedding_provider: Mapped[str] = mapped_column(String(length=100), nullable=False)

    project_id: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    asset_id: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    chunk_id: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    chunk_order: Mapped[int | None] = mapped_column(Integer, nullable=True)

    record_metadata: Mapped[dict[str, Any]] = mapped_column(
        'metadata',
        JSONB,
        default=dict,
        server_default=sql_text("'{}'::jsonb"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint('vector_record_uuid', name='uq_vector_records_uuid'),
        UniqueConstraint(
            'collection_name',
            'record_id',
            'embedding_provider',
            'embedding_model',
            'vector_size',
            name='uq_vector_records_collection_record_model',
        ),
        CheckConstraint(
            "char_length(btrim(collection_name)) > 0",
            name='ck_vector_records_collection_not_blank',
        ),
        CheckConstraint(
            "char_length(btrim(record_id)) > 0",
            name='ck_vector_records_record_id_not_blank',
        ),
        CheckConstraint(
            "char_length(btrim(text)) > 0",
            name='ck_vector_records_text_not_blank',
        ),
        CheckConstraint('vector_size > 0', name='ck_vector_records_vector_size_positive'),
        CheckConstraint(
            'vector_dims(embedding) = vector_size',
            name='ck_vector_records_embedding_dimensions',
        ),
        CheckConstraint(
            "char_length(btrim(embedding_model)) > 0",
            name='ck_vector_records_embedding_model_not_blank',
        ),
        CheckConstraint(
            "char_length(btrim(embedding_provider)) > 0",
            name='ck_vector_records_embedding_provider_not_blank',
        ),
        CheckConstraint(
            'chunk_order IS NULL OR chunk_order >= 0',
            name='ck_vector_records_chunk_order_non_negative',
        ),
        Index('ix_vector_records_collection_name', 'collection_name'),
        Index('ix_vector_records_vector_size', 'vector_size'),
        Index('ix_vector_records_project_id', 'project_id'),
        Index('ix_vector_records_asset_id', 'asset_id'),
        Index('ix_vector_records_chunk_id', 'chunk_id'),
        Index('ix_vector_records_embedding_model', 'embedding_model'),
        Index('ix_vector_records_embedding_provider', 'embedding_provider'),
        Index(
            'ix_vector_records_collection_vector_size_model',
            'collection_name',
            'vector_size',
            'embedding_provider',
            'embedding_model',
        ),
        Index('ix_vector_records_metadata_gin', 'metadata', postgresql_using='gin'),
    )
