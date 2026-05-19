from motor.motor_asyncio import AsyncIOMotorClient

from src.ragforge.core.config import Settings


class MongoDBClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.connection: AsyncIOMotorClient | None = None
        self.database = None

    async def connect(self):
        self.connection = AsyncIOMotorClient(self.settings.MONGODB_URL)
        self.database = self.connection[self.settings.MONGODB_DATABASE]

    async def close(self):
        if self.connection:
            self.connection.close()