from __future__ import annotations
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


"""
End-to-end validation for Branch 20 PostgreSQL production layer.

This script validates the architecture choices that matter:

- PostgreSQL connection works,
- UnitOfWork commits once,
- repositories can create project/assets/chunks,
- duplicate original asset names are allowed,
- stored filename uniqueness is enforced by PostgreSQL,
- chunk replacement is atomic,
- cleanup removes the validation project.
"""

import asyncio
from uuid import uuid4

from sqlalchemy.exc import IntegrityError

from src.ragforge.stores.postgres.session import (
    PostgresConnectionSettings,
    PostgresSessionManager,
    build_postgres_async_url,
)
from src.ragforge.stores.postgres.unit_of_work import PostgresUnitOfWork


async def validate() -> None:
    connection = PostgresConnectionSettings.from_env()
    manager = PostgresSessionManager(database_url=build_postgres_async_url(connection))
    project_id = f'branch20_postgres_{uuid4().hex[:8]}'

    await manager.ping()
    print('PostgreSQL ping succeeded.')

    async def cleanup_project() -> None:
        """Best-effort cleanup so failed validations do not pollute the database."""

        try:
            async with PostgresUnitOfWork(manager.session_factory) as cleanup_uow:
                assert cleanup_uow.projects is not None
                await cleanup_uow.projects.delete_by_public_project_id(project_id)
                await cleanup_uow.commit()
        except Exception:
            # Cleanup must not hide the original validation failure.
            pass

    try:
        async with PostgresUnitOfWork(manager.session_factory) as uow:
            assert uow.projects is not None
            assert uow.assets is not None
            assert uow.chunks is not None

            project = await uow.projects.get_or_create(project_id=project_id)

            asset_a = await uow.assets.create_asset(
                project_pk=project.pk,
                asset_type='file',
                asset_name='lesson.pdf',
                original_filename='lesson.pdf',
                stored_filename='uuid-a_lesson.pdf',
                storage_path=f'storage/uploads/{project_id}/uuid-a_lesson.pdf',
                mime_type='application/pdf',
                size_bytes=1024,
                asset_metadata={'validation': 'branch20', 'copy': 'a'},
            )
            asset_b = await uow.assets.create_asset(
                project_pk=project.pk,
                asset_type='file',
                asset_name='lesson.pdf',
                original_filename='lesson.pdf',
                stored_filename='uuid-b_lesson.pdf',
                storage_path=f'storage/uploads/{project_id}/uuid-b_lesson.pdf',
                mime_type='application/pdf',
                size_bytes=2048,
                asset_metadata={'validation': 'branch20', 'copy': 'b'},
            )

            inserted = await uow.chunks.replace_asset_chunks(
                project_pk=project.pk,
                asset_pk=asset_a.pk,
                chunks=[
                    {'chunk_text': 'First validated PostgreSQL chunk.', 'chunk_order': 1},
                    {'chunk_text': 'Second validated PostgreSQL chunk.', 'chunk_order': 2},
                ],
            )
            await uow.assets.update_processing_result(
                asset_pk=asset_a.pk,
                asset_status='processed',
                chunk_count=inserted,
                extraction_method='validation',
            )

            await uow.commit()

        async with PostgresUnitOfWork(manager.session_factory) as uow:
            assert uow.projects is not None
            assert uow.assets is not None
            assert uow.chunks is not None

            project = await uow.projects.get_by_public_project_id(project_id)
            assert project is not None

            assets = await uow.assets.list_project_assets(project_pk=project.pk, asset_type='file')
            assert len(assets) == 2, 'Two assets with the same original name should exist.'

            chunks = await uow.chunks.list_project_chunks(project_pk=project.pk)
            assert len(chunks) == 2, 'Two chunks should have been inserted.'

            await uow.commit()

        # Verify stored_filename uniqueness is enforced by the database.
        duplicate_blocked = False
        try:
            async with PostgresUnitOfWork(manager.session_factory) as uow:
                assert uow.projects is not None
                assert uow.assets is not None
                project = await uow.projects.get_by_public_project_id(project_id)
                assert project is not None
                await uow.assets.create_asset(
                    project_pk=project.pk,
                    asset_type='file',
                    asset_name='another-display-name.pdf',
                    original_filename='another-display-name.pdf',
                    stored_filename='uuid-a_lesson.pdf',
                    storage_path=f'storage/uploads/{project_id}/another-path.pdf',
                )
                await uow.commit()
        except IntegrityError:
            duplicate_blocked = True

        assert duplicate_blocked, 'Duplicate stored_filename should be blocked.'

        # Verify storage_path uniqueness is also enforced by the database.
        duplicate_path_blocked = False
        try:
            async with PostgresUnitOfWork(manager.session_factory) as uow:
                assert uow.projects is not None
                assert uow.assets is not None
                project = await uow.projects.get_by_public_project_id(project_id)
                assert project is not None
                await uow.assets.create_asset(
                    project_pk=project.pk,
                    asset_type='file',
                    asset_name='third-display-name.pdf',
                    original_filename='third-display-name.pdf',
                    stored_filename='uuid-c_lesson.pdf',
                    storage_path=f'storage/uploads/{project_id}/uuid-a_lesson.pdf',
                )
                await uow.commit()
        except IntegrityError:
            duplicate_path_blocked = True

        assert duplicate_path_blocked, 'Duplicate storage_path should be blocked.'

        # Cleanup validation project. Cascades delete assets and chunks.
        async with PostgresUnitOfWork(manager.session_factory) as uow:
            assert uow.projects is not None
            deleted = await uow.projects.delete_by_public_project_id(project_id)
            assert deleted == 1
            await uow.commit()

        print('Branch 20 PostgreSQL production-layer validation passed.')
    finally:
        await cleanup_project()
        await manager.dispose()


def main() -> None:
    asyncio.run(validate())


if __name__ == '__main__':
    main()
