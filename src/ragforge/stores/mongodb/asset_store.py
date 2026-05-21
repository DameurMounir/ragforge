from datetime import datetime, timezone
from bson import ObjectId

from src.ragforge.models.enums.asset_status import AssetStatus

from src.ragforge.models.db_schemes import Asset
from src.ragforge.stores.mongodb.base_store import BaseMongoStore
from src.ragforge.stores.mongodb.collections import MongoCollection


class AssetStore(BaseMongoStore):
    """
    MongoDB store for asset records.
    """

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[MongoCollection.ASSETS.value]

    async def create_asset(self, asset: Asset) -> Asset:
        """
        Insert a new asset record.
        """
        result = await self.collection.insert_one(
            asset.model_dump(by_alias=True, exclude_unset=True)
        )
        asset.id = result.inserted_id

        return asset

    async def get_asset_by_id(self, asset_id: str | ObjectId) -> Asset | None:
        """
        Return an asset by MongoDB ObjectId.
        """
        object_id = ObjectId(asset_id) if isinstance(asset_id, str) else asset_id

        record = await self.collection.find_one({'_id': object_id})

        if record is None:
            return None

        return Asset(**record)

    async def get_project_assets(
        self,
        asset_project_id: str | ObjectId,
        asset_type: str | None = None,
    ) -> list[Asset]:
        """
        Return all assets belonging to a project.
        """
        object_id = (
            ObjectId(asset_project_id)
            if isinstance(asset_project_id, str)
            else asset_project_id
        )

        query = {'asset_project_id': object_id}

        if asset_type is not None:
            query['asset_type'] = asset_type

        records = await self.collection.find(query).to_list(length=None)

        return [
            Asset(**record)
            for record in records
        ]

    async def get_asset_record(
        self,
        asset_project_id: str | ObjectId,
        asset_name: str,
    ) -> Asset | None:
        """
        Return an asset by project id and asset name.
        """
        object_id = (
            ObjectId(asset_project_id)
            if isinstance(asset_project_id, str)
            else asset_project_id
        )

        record = await self.collection.find_one(
            {
                'asset_project_id': object_id,
                'asset_name': asset_name,
            }
        )

        if record is None:
            return None

        return Asset(**record)

    
    async def get_uploaded_assets_by_project_id(
        self,
        asset_project_id: str | ObjectId,
    ) -> list[Asset]:
        """
        Return all uploaded assets belonging to a project.

        Branch 12 uses this method to find assets that still need processing.
        """
        object_id = (
            ObjectId(asset_project_id)
            if isinstance(asset_project_id, str)
            else asset_project_id
        )

        records = await self.collection.find({
            'asset_project_id': object_id,
            'asset_status': AssetStatus.UPLOADED.value,
        }).to_list(length=None)

        return [
            Asset(**record)
            for record in records
        ]
    
    async def update_asset_processing_result(
        self,
        asset_id: str | ObjectId,
        asset_status: str,
        chunk_count: int = 0,
        extraction_method: str | None = None,
        extraction_error: str | None = None,
    ) -> bool:
        """
        Update asset processing result after document processing.

        Branch 12 uses this method to mark assets as processed or failed.
        """
        object_id = (
            ObjectId(asset_id)
            if isinstance(asset_id, str)
            else asset_id
        )

        result = await self.collection.update_one(
            {'_id': object_id},
            {
                '$set': {
                    'asset_status': asset_status,
                    'chunk_count': chunk_count,
                    'extraction_method': extraction_method,
                    'extraction_error': extraction_error,
                    'updated_at': datetime.now(timezone.utc),
                }
            },
        )

        return result.modified_count > 0

    
    @classmethod
    async def create_instance(cls, db_client: object):
        """
        Create store instance and initialize collection indexes./Branch 11
        """
        instance = cls(db_client=db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self) -> None:
        """
        Initialize MongoDB indexes for the assets collection.
        """
        for index in Asset.get_indexes():
            await self.collection.create_index(
                index['key'],
                name=index['name'],
                unique=index['unique'],
            )