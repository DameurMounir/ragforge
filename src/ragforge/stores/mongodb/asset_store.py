from bson.objectid import ObjectId

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