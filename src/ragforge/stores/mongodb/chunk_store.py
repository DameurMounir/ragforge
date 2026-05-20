from bson.objectid import ObjectId
from pymongo import InsertOne

from src.ragforge.models.db_schemes import DataChunk
from src.ragforge.stores.mongodb.base_store import BaseMongoStore
from src.ragforge.stores.mongodb.collections import MongoCollection


class ChunkStore(BaseMongoStore):
    """
    MongoDB store for data chunk records.
    """

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[MongoCollection.DATA_CHUNKS.value]

    async def create_chunk(self, chunk: DataChunk) -> DataChunk:
        """
        Insert one data chunk.
        """
        result = await self.collection.insert_one(
            chunk.model_dump(by_alias=True, exclude_unset=True)
        )
        chunk.id = result.inserted_id

        return chunk

    async def get_chunk(self, chunk_id: str | ObjectId) -> DataChunk | None:
        """
        Return a chunk by MongoDB ObjectId.
        """
        object_id = ObjectId(chunk_id) if isinstance(chunk_id, str) else chunk_id

        record = await self.collection.find_one({'_id': object_id})

        if record is None:
            return None

        return DataChunk(**record)

    async def insert_many_chunks(
        self,
        chunks: list[DataChunk],
        batch_size: int = 100,
    ) -> int:
        """
        Insert chunks in batches.
        """
        if not chunks:
            return 0

        inserted_count = 0

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]

            operations = [
                InsertOne(chunk.model_dump(by_alias=True, exclude_unset=True))
                for chunk in batch
            ]

            if operations:
                result = await self.collection.bulk_write(operations)
                inserted_count += result.inserted_count

        return inserted_count

    async def get_asset_chunks(
        self,
        asset_id: str | ObjectId,
    ) -> list[DataChunk]:
        """
        Return all chunks belonging to one asset.
        """
        object_id = ObjectId(asset_id) if isinstance(asset_id, str) else asset_id

        cursor = self.collection.find(
            {'chunk_asset_id': object_id}
        ).sort('chunk_order', 1)

        chunks = []

        async for record in cursor:
            chunks.append(DataChunk(**record))

        return chunks

    async def delete_chunks_by_project_id(
        self,
        project_id: str | ObjectId,
    ) -> int:
        """
        Delete all chunks belonging to a project.
        """
        object_id = ObjectId(project_id) if isinstance(project_id, str) else project_id

        result = await self.collection.delete_many(
            {'chunk_project_id': object_id}
        )

        return result.deleted_count

    async def delete_chunks_by_asset_id(
        self,
        asset_id: str | ObjectId,
    ) -> int:
        """
        Delete all chunks belonging to one asset.
        """
        object_id = ObjectId(asset_id) if isinstance(asset_id, str) else asset_id

        result = await self.collection.delete_many(
            {'chunk_asset_id': object_id}
        )

        return result.deleted_count