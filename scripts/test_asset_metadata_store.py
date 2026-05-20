import asyncio

from motor.motor_asyncio import AsyncIOMotorClient

from src.ragforge.core.config import get_settings
from src.ragforge.models.db_schemes import Asset, DataChunk
from src.ragforge.models.enums.asset_status import AssetStatus
from src.ragforge.models.enums.asset_type import AssetType
from src.ragforge.stores.mongodb import AssetStore, ChunkStore, ProjectStore


async def main():
    settings = get_settings()

    mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
    db_client = mongo_client[settings.MONGODB_DATABASE]

    project_store = ProjectStore(db_client=db_client)
    asset_store = AssetStore(db_client=db_client)
    chunk_store = ChunkStore(db_client=db_client)

    project = await project_store.get_project_or_create_one(
        project_id='testproject10'
    )

    print('Project created/found:')
    print(project)

    asset = Asset(
        asset_project_id=project.id,
        asset_type=AssetType.FILE,
        asset_status=AssetStatus.UPLOADED,
        asset_name='branch10_test_file.pdf',
        file_name='branch10_test_file.pdf',
        file_extension='pdf',
        mime_type='application/pdf',
        asset_size=1024,
        storage_path='storage/uploads/testproject10/documents/branch10_test_file.pdf',
        asset_metadata={
            'test_branch': 'branch_10',
            'purpose': 'manual_store_validation',
        },
    )

    asset = await asset_store.create_asset(asset=asset)

    print('Asset created:')
    print(asset)

    chunk = DataChunk(
        chunk_text='This is a test chunk created from Branch 10 metadata store.',
        chunk_metadata={
            'page': 1,
            'source': 'manual_test',
        },
        chunk_order=1,
        chunk_project_id=project.id,
        chunk_asset_id=asset.id,
    )

    chunk = await chunk_store.create_chunk(chunk=chunk)

    print('Chunk created:')
    print(chunk)

    chunks = await chunk_store.get_asset_chunks(asset_id=asset.id)

    print(f'Chunks found for asset: {len(chunks)}')
    for item in chunks:
        print(item)

    mongo_client.close()


if __name__ == '__main__':
    asyncio.run(main())
