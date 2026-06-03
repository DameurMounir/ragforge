from bson.objectid import ObjectId
from pymongo import InsertOne, UpdateOne

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

    @classmethod
    async def create_instance(cls, db_client: object):
        """
        Create store instance and initialize collection indexes.
        """
        instance = cls(db_client=db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self) -> None:
        """
        Initialize MongoDB indexes for the data_chunks collection.
        """
        for index in DataChunk.get_indexes():
            await self.collection.create_index(
                index['key'],
                name=index['name'],
                unique=index['unique'],
            )

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
        Insert multiple chunks in batches.

        Returns the number of inserted chunks.
        """
        if not chunks:
            return 0

        if batch_size <= 0:
            raise ValueError('batch_size must be greater than 0')

        inserted_count = 0

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]

            operations = [
                InsertOne(chunk.model_dump(by_alias=True, exclude_unset=True))
                for chunk in batch
            ]

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
    
    async def get_project_chunks(
        self,
        project_id: str | ObjectId,
        asset_id: str | ObjectId | None = None,
        only_not_embedded: bool = False,
        limit: int | None = None,
    ) -> list[DataChunk]:
        """
        Return chunks for a project, optionally filtered by asset.

        Branch 16 uses this method to load chunks for embedding/indexing.
        """
        object_project_id = (
            ObjectId(project_id)
            if isinstance(project_id, str)
            else project_id
        )

        query = {'chunk_project_id': object_project_id}

        if asset_id is not None:
            object_asset_id = (
                ObjectId(asset_id)
                if isinstance(asset_id, str)
                else asset_id
            )
            query['chunk_asset_id'] = object_asset_id

        if only_not_embedded:
            query['embedded'] = False

        cursor = self.collection.find(query).sort(
            [
                ('chunk_asset_id', 1),
                ('chunk_order', 1),
            ]
        )

        if limit is not None:
            cursor = cursor.limit(limit)

        chunks = []

        async for record in cursor:
            chunks.append(DataChunk(**record))

        return chunks

    async def mark_chunks_embedded(
        self,
        indexed_chunks: list[dict],
    ) -> int:
        """
        Mark chunks as embedded after successful vector insertion.

        Expected item shape:
        {
            'chunk_id': ObjectId,
            'embedding_model': 'embedding-model-name',
            'vector_id': '...'
        }
        """
        if not indexed_chunks:
            return 0

        operations = []

        for item in indexed_chunks:
            chunk_id = item['chunk_id']

            object_id = (
                ObjectId(chunk_id)
                if isinstance(chunk_id, str)
                else chunk_id
            )

            operations.append(
                UpdateOne(
                    {'_id': object_id},
                    {
                        '$set': {
                            'embedded': True,
                            'embedding_model': item['embedding_model'],
                            'vector_id': item['vector_id'],
                        }
                    },
                )
            )

        result = await self.collection.bulk_write(operations)

        return result.modified_count

    async def delete_chunks_by_project_id(
        self,
        project_id: str | ObjectId,
    ) -> int:
        """
        Delete all chunks belonging to one project.
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