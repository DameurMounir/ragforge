from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.ragforge.stores.postgres.models.project import ProjectTable
from src.ragforge.stores.postgres.records import ProjectRecord
from src.ragforge.stores.postgres.repositories.mappers import project_to_record


class PostgresProjectRepository:
    """
    PostgreSQL repository for project metadata.

    This repository does not commit. Transaction ownership belongs to
    PostgresUnitOfWork or the calling service layer.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_pk(self, project_pk: int) -> ProjectRecord | None:
        result = await self.session.execute(
            select(ProjectTable).where(ProjectTable.id == project_pk)
        )
        row = result.scalar_one_or_none()
        return project_to_record(row) if row is not None else None

    async def get_by_public_project_id(self, project_id: str) -> ProjectRecord | None:
        result = await self.session.execute(
            select(ProjectTable).where(ProjectTable.project_id == project_id)
        )
        row = result.scalar_one_or_none()
        return project_to_record(row) if row is not None else None

    async def get_or_create(self, project_id: str) -> ProjectRecord:
        """
        Concurrency-safe get-or-create using PostgreSQL ON CONFLICT.

        Two concurrent requests for the same project will not create duplicates.
        The winner inserts the row; the other request reloads the existing row.
        """

        stmt = (
            insert(ProjectTable)
            .values(project_id=project_id)
            .on_conflict_do_nothing(index_elements=['project_id'])
            .returning(ProjectTable.id)
        )
        result = await self.session.execute(stmt)
        inserted_id = result.scalar_one_or_none()

        if inserted_id is not None:
            project = await self.get_by_pk(project_pk=int(inserted_id))
            if project is None:
                raise RuntimeError('Inserted project could not be reloaded.')
            return project

        existing = await self.get_by_public_project_id(project_id=project_id)
        if existing is None:
            raise RuntimeError('Project get-or-create failed unexpectedly.')
        return existing

    async def list_projects(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> list[ProjectRecord]:
        safe_page = max(page, 1)
        safe_page_size = min(max(page_size, 1), 100)
        offset = (safe_page - 1) * safe_page_size

        result = await self.session.execute(
            select(ProjectTable)
            .order_by(ProjectTable.id.desc())
            .offset(offset)
            .limit(safe_page_size)
        )
        return [project_to_record(row) for row in result.scalars().all()]

    async def delete_by_public_project_id(self, project_id: str) -> int:
        result = await self.session.execute(
            delete(ProjectTable).where(ProjectTable.project_id == project_id)
        )
        await self.session.flush()
        return int(result.rowcount or 0)
