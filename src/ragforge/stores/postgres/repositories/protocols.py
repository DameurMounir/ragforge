from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID

from src.ragforge.stores.postgres.records import (
    AssetRecord,
    DataChunkRecord,
    ProjectRecord,
)


class ProjectRepositoryProtocol(Protocol):
    """
    ORM-neutral contract for project persistence.

    Implementations should return ProjectRecord values rather than ORM-specific objects.
    """

    async def get_by_public_project_id(self, project_id: str) -> ProjectRecord | None: ...

    async def get_or_create(self, project_id: str) -> ProjectRecord: ...


class AssetRepositoryProtocol(Protocol):
    """ORM-neutral contract for asset persistence."""

    async def create_asset(
        self,
        project_pk: int,
        asset_type: str,
        asset_name: str,
        **kwargs: Any,
    ) -> AssetRecord: ...

    async def get_by_pk(self, asset_pk: int) -> AssetRecord | None: ...

    async def get_by_asset_uuid(self, asset_uuid: UUID) -> AssetRecord | None: ...

    async def get_by_stored_filename(
        self,
        project_pk: int,
        stored_filename: str,
    ) -> AssetRecord | None: ...

    async def list_project_assets(
        self,
        project_pk: int,
        asset_type: str | None = None,
    ) -> list[AssetRecord]: ...


class ChunkRepositoryProtocol(Protocol):
    """ORM-neutral contract for chunk persistence."""

    async def replace_asset_chunks(
        self,
        project_pk: int,
        asset_pk: int,
        chunks: list[dict[str, Any]],
    ) -> int: ...

    async def list_project_chunks(
        self,
        project_pk: int,
        limit: int | None = None,
    ) -> list[DataChunkRecord]: ...
