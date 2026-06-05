from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.ragforge.stores.postgres.models.base import Base
from src.ragforge.stores.postgres.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from src.ragforge.stores.postgres.models.asset import AssetTable
    from src.ragforge.stores.postgres.models.data_chunk import DataChunkTable


class ProjectTable(TimestampMixin, Base):
    """
    Relational representation of a RAGForge project.

    `id` is the internal relational primary key.
    `project_id` preserves the current API-level project identifier.
    `project_uuid` is a stable UUID suitable for future public references.
    """

    __tablename__ = 'projects'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        server_default=text('gen_random_uuid()'),
        nullable=False,
    )
    project_id: Mapped[str] = mapped_column(String(length=150), nullable=False)

    assets: Mapped[list['AssetTable']] = relationship(
        back_populates='project',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )
    chunks: Mapped[list['DataChunkTable']] = relationship(
        back_populates='project',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    __table_args__ = (
        UniqueConstraint('project_uuid', name='uq_projects_project_uuid'),
        UniqueConstraint('project_id', name='uq_projects_project_id'),
    )
