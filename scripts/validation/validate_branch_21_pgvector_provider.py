from __future__ import annotations

import asyncio
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv
from sqlalchemy import text

from src.ragforge.core.config import get_settings
from src.ragforge.providers.vector_db.implementations.pgvector_provider import (
    PgVectorProvider,
)
from src.ragforge.providers.vector_db.schemas import VectorRecord
from src.ragforge.stores.postgres.session import PostgresSessionManager

load_dotenv(ROOT_DIR / '.env')


async def main() -> None:
    settings = get_settings()
    session_manager = PostgresSessionManager.from_settings(settings)
    table_name = settings.PGVECTOR_TABLE_NAME
    vector_size = settings.PGVECTOR_EFFECTIVE_VECTOR_SIZE

    provider = PgVectorProvider(
        session_manager=session_manager,
        table_name=table_name,
        vector_size=vector_size,
        distance=settings.PGVECTOR_DISTANCE,
        index_type=settings.PGVECTOR_INDEX_TYPE,
        index_vector_type=settings.PGVECTOR_INDEX_VECTOR_TYPE,
        hnsw_m=settings.PGVECTOR_HNSW_M,
        hnsw_ef_construction=settings.PGVECTOR_HNSW_EF_CONSTRUCTION,
        hnsw_ef_search=settings.PGVECTOR_HNSW_EF_SEARCH,
        ivfflat_lists=settings.PGVECTOR_IVFFLAT_LISTS,
        ivfflat_probes=settings.PGVECTOR_IVFFLAT_PROBES,
        index_min_records=settings.PGVECTOR_INDEX_MIN_RECORDS,
        auto_create_index=settings.PGVECTOR_AUTO_CREATE_INDEX,
        create_extension_on_startup=settings.PGVECTOR_CREATE_EXTENSION_ON_STARTUP,
        embedding_model=settings.EMBEDDING_MODEL,
        embedding_provider=settings.EMBEDDING_PROVIDER,
    )

    collection_name = 'branch21_validation_collection'

    await provider.connect()
    try:
        async with session_manager.session() as session:
            await session.execute(text('SELECT 1'))
            print('PostgreSQL ping succeeded.')

            extension = await session.execute(
                text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
            )
            assert extension.scalar_one_or_none() == 'vector'
            print('PgVector extension exists.')

            table = await session.execute(
                text(
                    'SELECT table_name FROM information_schema.tables '
                    'WHERE table_name = :table_name'
                ),
                {'table_name': table_name},
            )
            assert table.scalar_one_or_none() == table_name
            print(f'{table_name} table exists.')

        await provider.create_collection(
            collection_name=collection_name,
            vector_size=vector_size,
            distance=provider.distance,
            do_reset=True,
        )

        async with session_manager.session() as session:
            index = await session.execute(
                text(
                    'SELECT indexname FROM pg_indexes '
                    'WHERE tablename = :table_name '
                    'AND indexname = :index_name'
                ),
                {
                    'table_name': table_name,
                    'index_name': provider._index_name(),
                },
            )
            assert index.scalar_one_or_none() == provider._index_name()
            print('Configured PgVector index exists.')

        base_vector = [0.0] * vector_size
        near_vector = base_vector.copy()
        near_vector[0] = 1.0
        far_vector = base_vector.copy()
        far_vector[min(1, vector_size - 1)] = 1.0

        inserted = await provider.insert_many(
            collection_name=collection_name,
            records=[
                VectorRecord(
                    record_id='near',
                    vector=near_vector,
                    text='near vector validation record',
                    metadata={
                        'project_id': 'branch21-project',
                        'asset_id': 'asset-a',
                        'chunk_id': 'chunk-near',
                        'chunk_order': 0,
                        'embedding_model': settings.EMBEDDING_MODEL,
                        'embedding_provider': settings.EMBEDDING_PROVIDER,
                    },
                ),
                VectorRecord(
                    record_id='far',
                    vector=far_vector,
                    text='far vector validation record',
                    metadata={
                        'project_id': 'branch21-project',
                        'asset_id': 'asset-a',
                        'chunk_id': 'chunk-far',
                        'chunk_order': 1,
                        'embedding_model': settings.EMBEDDING_MODEL,
                        'embedding_provider': settings.EMBEDDING_PROVIDER,
                    },
                ),
            ],
            batch_size=2,
        )
        assert inserted == 2
        print('PgVector insert_many succeeded.')

        results = await provider.search_by_vector(
            collection_name=collection_name,
            vector=near_vector,
            limit=2,
            filters={'project_id': 'branch21-project'},
        )
        assert len(results) == 2
        assert results[0].record_id == 'near'
        assert results[0].score is not None
        assert results[0].score >= results[1].score
        print('PgVector search_by_vector succeeded.')

        await provider.delete_collection(collection_name=collection_name)
        print('Branch 21 PgVector provider validation passed.')
    finally:
        await provider.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
