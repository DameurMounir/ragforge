import asyncio

from src.ragforge.core.config import get_settings
from src.ragforge.models.db_schemes import Asset, DataChunk
from src.ragforge.models.enums.asset_status import AssetStatus
from src.ragforge.models.enums.asset_type import AssetType
from src.ragforge.stores.mongodb import AssetStore, ChunkStore, ProjectStore
from src.ragforge.stores.mongodb.client import MongoDBClient


async def main() -> None:
    settings = get_settings()

    mongodb_client = MongoDBClient(settings=settings)
    await mongodb_client.connect()

    db_client = mongodb_client.database

    project_store = await ProjectStore.create_instance(db_client=db_client)
    asset_store = await AssetStore.create_instance(db_client=db_client)
    chunk_store = await ChunkStore.create_instance(db_client=db_client)

    project_id = 'branch12_test_project'

    project = await project_store.get_project_or_create_one(
        project_id=project_id
    )

    print('Project OK:', project.project_id, project.id)

    asset = Asset(
        asset_project_id=project.id,
        asset_type=AssetType.FILE.value,
        asset_status=AssetStatus.UPLOADED.value,
        asset_name='branch12_test_file.txt',
        source_uri='storage/uploads/branch12_test_project/documents/branch12_test_file.txt',
        file_name='branch12_test_file.txt',
        file_extension='txt',
        mime_type='text/plain',
        asset_size=120,
        storage_path='storage/uploads/branch12_test_project/documents/branch12_test_file.txt',
    )

    existing_asset = await asset_store.get_asset_record(
        asset_project_id=project.id,
        asset_name=asset.asset_name,
    )

    if existing_asset is not None:
        asset = existing_asset
        print('Asset already exists:', asset.id)
    else:
        asset = await asset_store.create_asset(asset=asset)
        print('Asset created:', asset.id)

    uploaded_assets = await asset_store.get_uploaded_assets_by_project_id(
        asset_project_id=project.id
    )

    print('Uploaded assets found:', len(uploaded_assets))

    await chunk_store.delete_chunks_by_asset_id(
        asset_id=asset.id
    )

    chunks = [
        DataChunk(
            chunk_text='This is Branch 12 test chunk 1.',
            chunk_metadata={
                'source': 'manual_branch12_test',
                'order': 1,
            },
            chunk_order=1,
            chunk_project_id=project.id,
            chunk_asset_id=asset.id,
            embedded=False,
        ),
        DataChunk(
            chunk_text='This is Branch 12 test chunk 2.',
            chunk_metadata={
                'source': 'manual_branch12_test',
                'order': 2,
            },
            chunk_order=2,
            chunk_project_id=project.id,
            chunk_asset_id=asset.id,
            embedded=False,
        ),
    ]

    inserted_count = await chunk_store.insert_many_chunks(
        chunks=chunks
    )

    print('Chunks inserted:', inserted_count)

    await asset_store.update_asset_processing_result(
        asset_id=asset.id,
        asset_status=AssetStatus.PROCESSED.value,
        chunk_count=inserted_count,
        extraction_method='manual_branch12_test',
        extraction_error=None,
    )

    updated_asset = await asset_store.get_asset_by_id(
        asset_id=asset.id
    )

    print('Asset status:', updated_asset.asset_status)
    print('Asset chunk count:', updated_asset.chunk_count)

    asset_chunks = await chunk_store.get_asset_chunks(
        asset_id=asset.id
    )

    print('Chunks found for asset:', len(asset_chunks))

    await mongodb_client.close()

    print('Branch 12 metadata persistence test OK.')


if __name__ == '__main__':
    asyncio.run(main())