from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from src.ragforge.core.config import get_settings
from src.ragforge.providers.vector_db.schemas import VectorRecord
from src.ragforge.services.vector_db_service import VectorDBService


def main() -> None:
    settings = get_settings()

    collection_name = 'ragforge_branch15_validation'
    vector_size = 4

    service = VectorDBService(settings=settings)

    try:
        print('Connecting to vector DB...')
        service.connect()
        print('Qdrant connection OK')

        print('Creating validation collection...')
        created = service.ensure_collection(
            collection_name=collection_name,
            vector_size=vector_size,
            distance='cosine',
            do_reset=True,
        )
        print(f'Collection created: {created}')

        one_record = VectorRecord(
            record_id='branch15_single_record',
            vector=[0.10, 0.20, 0.30, 0.40],
            text='RAGForge Branch 15 single validation vector.',
            metadata={
                'project_id': 'branch15_project',
                'asset_id': 'branch15_asset_single',
                'chunk_id': 'branch15_chunk_single',
                'source': 'validation_script',
            },
        )

        print('Inserting one vector...')
        service.insert_one(
            collection_name=collection_name,
            record=one_record,
        )
        print('Inserted one vector')

        batch_records = [
            VectorRecord(
                record_id='branch15_batch_record_1',
                vector=[0.11, 0.21, 0.31, 0.41],
                text='RAGForge Branch 15 batch validation vector 1.',
                metadata={
                    'project_id': 'branch15_project',
                    'asset_id': 'branch15_asset_batch',
                    'chunk_id': 'branch15_chunk_1',
                    'source': 'validation_script',
                },
            ),
            VectorRecord(
                record_id='branch15_batch_record_2',
                vector=[0.90, 0.10, 0.10, 0.10],
                text='A different validation vector for search comparison.',
                metadata={
                    'project_id': 'branch15_project',
                    'asset_id': 'branch15_asset_batch',
                    'chunk_id': 'branch15_chunk_2',
                    'source': 'validation_script',
                },
            ),
        ]

        print('Inserting batch vectors...')
        inserted = service.insert_many(
            collection_name=collection_name,
            records=batch_records,
            batch_size=2,
        )
        print(f'Inserted batch vectors: {inserted}')

        print('Searching by vector...')
        results = service.search_by_vector(
            collection_name=collection_name,
            vector=[0.10, 0.20, 0.30, 0.40],
            limit=3,
            filters={'project_id': 'branch15_project'},
        )

        print(f'Search returned {len(results)} result(s)')

        for index, result in enumerate(results, start=1):
            print(
                f'{index}. '
                f'record_id={result.record_id} | '
                f'score={result.score} | '
                f'text={result.text}'
            )

        if not results:
            raise RuntimeError('Vector search returned no results.')

        print('Deleting validation collection...')
        deleted = service.delete_collection(collection_name=collection_name)
        print(f'Collection deleted: {deleted}')

        print('Branch 15 validation passed')

    finally:
        service.close()


if __name__ == '__main__':
    main()