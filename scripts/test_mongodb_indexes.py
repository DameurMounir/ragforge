import asyncio

from motor.motor_asyncio import AsyncIOMotorClient

from src.ragforge.core.config import get_settings
from src.ragforge.stores.mongodb import AssetStore, ChunkStore, ProjectStore


async def main() -> None:
    settings = get_settings()

    mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
    db_client = mongo_client[settings.MONGODB_DATABASE]

    await ProjectStore.create_instance(db_client=db_client)
    await AssetStore.create_instance(db_client=db_client)
    await ChunkStore.create_instance(db_client=db_client)

    print('MongoDB authenticated connection OK.')
    print('MongoDB metadata indexes initialized successfully.')

    mongo_client.close()


if __name__ == '__main__':
    asyncio.run(main())
