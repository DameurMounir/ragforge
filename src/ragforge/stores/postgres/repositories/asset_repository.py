from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.ragforge.stores.postgres.models.asset import AssetTable
from src.ragforge.stores.postgres.records import AssetRecord
from src.ragforge.stores.postgres.repositories.mappers import asset_to_record


class PostgresAssetRepository:
    """
    PostgreSQL repository for asset metadata.

    This repository does not commit. Transaction ownership belongs to
    PostgresUnitOfWork or the calling service layer.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_asset(
        self,
        project_pk: int,
        asset_type: str,
        asset_name: str,
        original_filename: str | None = None,
        stored_filename: str | None = None,
        mime_type: str | None = None,
        size_bytes: int | None = None,
        storage_path: str | None = None,
        asset_status: str = 'uploaded',
        asset_metadata: dict[str, Any] | None = None,
    ) -> AssetRecord:
        """
        Create an asset row and return a domain record.

        `asset_name` is not unique. The database protects `stored_filename` and
        `storage_path` uniqueness per project when those values are present.
        """

        stmt = (
            insert(AssetTable)
            .values(
                project_pk=project_pk,
                asset_type=asset_type,
                asset_name=asset_name,
                original_filename=original_filename,
                stored_filename=stored_filename,
                mime_type=mime_type,
                size_bytes=size_bytes,
                storage_path=storage_path,
                asset_status=asset_status,
                asset_metadata=asset_metadata or {},
            )
            .returning(AssetTable)
        )
        result = await self.session.execute(stmt)
        row = result.scalar_one()
        await self.session.flush()
        return asset_to_record(row)

    async def get_by_pk(self, asset_pk: int) -> AssetRecord | None:
        result = await self.session.execute(
            select(AssetTable).where(AssetTable.id == asset_pk)
        )
        row = result.scalar_one_or_none()
        return asset_to_record(row) if row is not None else None

    async def get_by_asset_uuid(self, asset_uuid: UUID) -> AssetRecord | None:
        result = await self.session.execute(
            select(AssetTable).where(AssetTable.asset_uuid == asset_uuid)
        )
        row = result.scalar_one_or_none()
        return asset_to_record(row) if row is not None else None

    async def get_by_stored_filename(
        self,
        project_pk: int,
        stored_filename: str,
    ) -> AssetRecord | None:
        result = await self.session.execute(
            select(AssetTable).where(
                AssetTable.project_pk == project_pk,
                AssetTable.stored_filename == stored_filename,
            )
        )
        row = result.scalar_one_or_none()
        return asset_to_record(row) if row is not None else None

    async def get_by_storage_path(
        self,
        project_pk: int,
        storage_path: str,
    ) -> AssetRecord | None:
        result = await self.session.execute(
            select(AssetTable).where(
                AssetTable.project_pk == project_pk,
                AssetTable.storage_path == storage_path,
            )
        )
        row = result.scalar_one_or_none()
        return asset_to_record(row) if row is not None else None

    async def list_project_assets(
        self,
        project_pk: int,
        asset_type: str | None = None,
    ) -> list[AssetRecord]:
        query = select(AssetTable).where(AssetTable.project_pk == project_pk)

        if asset_type is not None:
            query = query.where(AssetTable.asset_type == asset_type)

        result = await self.session.execute(query.order_by(AssetTable.id.asc()))
        return [asset_to_record(row) for row in result.scalars().all()]

    async def update_processing_result(
        self,
        asset_pk: int,
        asset_status: str,
        chunk_count: int,
        extraction_method: str | None = None,
        extraction_error: str | None = None,
    ) -> AssetRecord:
        """
        Update processing metadata after a chunk replacement operation.
        """

        stmt = (
            update(AssetTable)
            .where(AssetTable.id == asset_pk)
            .values(
                asset_status=asset_status,
                chunk_count=chunk_count,
                extraction_method=extraction_method,
                extraction_error=extraction_error,
            )
            .returning(AssetTable)
        )
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            raise RuntimeError(f'Asset not found for processing update: {asset_pk}')
        await self.session.flush()
        return asset_to_record(row)
