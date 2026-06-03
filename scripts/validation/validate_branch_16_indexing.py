from pathlib import Path
import asyncio
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from src.ragforge.core.config import get_settings
from src.ragforge.schemas.indexing import IndexingRequest
from src.ragforge.services.indexing_service import IndexingService
from src.ragforge.stores.mongodb.chunk_store import ChunkStore
from src.ragforge.stores.mongodb.project_store import ProjectStore
from src.ragforge.stores.mongodb.client import MongoDBClient


async def main() -> None:
    settings = get_settings()

    project_id = 'project16test'

    mongodb_client = MongoDBClient(settings=settings)
    await mongodb_client.connect()

    try:
        db_client = mongodb_client.database

        project_store = await ProjectStore.create_instance(
            db_client=db_client
        )
        chunk_store = await ChunkStore.create_instance(
            db_client=db_client
        )

        project = await project_store.get_project_by_project_id(
            project_id=project_id
        )

        if project is None:
            raise RuntimeError(
                f'Project {project_id} not found. '
                'Upload and process documents before running Branch 16 validation.'
            )

        chunks = await chunk_store.get_project_chunks(
            project_id=project.id,
            only_not_embedded=False,
            limit=5,
        )

        if not chunks:
            raise RuntimeError(
                f'Project {project_id} has no chunks. '
                'Run /api/v1/documents/process/{project_id} first.'
            )

        indexing_service = IndexingService(settings=settings)

        status_code, response = await indexing_service.index_project_chunks(
            project_id=project_id,
            indexing_request=IndexingRequest(
                do_reset=True,
                batch_size=2,
                limit=5,
                include_results=True,
            ),
            project_store=project_store,
            chunk_store=chunk_store,
        )

        print(f'Status code: {status_code}')
        print(response)

        if status_code != 200:
            raise RuntimeError('Branch 16 indexing validation failed.')

        if response['indexed_chunks'] <= 0:
            raise RuntimeError('No chunks were indexed.')

        print('Branch 16 indexing validation passed')

    finally:
        await mongodb_client.close()


if __name__ == '__main__':
    asyncio.run(main())
