from datetime import datetime, timezone
from typing import Optional

from bson.objectid import ObjectId
from pydantic import BaseModel, ConfigDict, Field

from src.ragforge.models.enums.asset_status import AssetStatus
from src.ragforge.models.enums.asset_type import AssetType


def utc_now() -> datetime:
    """
    Return a timezone-aware UTC datetime.
    """
    return datetime.now(timezone.utc)


class Asset(BaseModel):
    """
    Database scheme representing a project asset.

    An asset can be a file, URL, image, video, audio source, web page,
    or any future knowledge source that can be processed into chunks.
    """

    id: Optional[ObjectId] = Field(default=None, alias='_id')

    asset_project_id: ObjectId
    asset_type: AssetType = AssetType.FILE
    asset_status: AssetStatus = AssetStatus.UPLOADED

    asset_name: str = Field(..., min_length=1)

    source_uri: Optional[str] = None

    file_name: Optional[str] = None
    file_extension: Optional[str] = None
    mime_type: Optional[str] = None
    asset_size: Optional[int] = Field(default=None, ge=0)
    storage_path: Optional[str] = None

    chunk_count: int = Field(default=0, ge=0)

    extraction_method: Optional[str] = None
    extraction_error: Optional[str] = None

    asset_config: dict = Field(default_factory=dict)
    asset_metadata: dict = Field(default_factory=dict)

    asset_pushed_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    
    @classmethod
    def get_indexes(cls) -> list[dict]:
        """
        Return MongoDB indexes required for the assets collection./Branch 11

        These indexes prepare future queries like: 
            get all project assets
            find asset by name
            filter assets by status
            filter assets by type
            find URL/web assets later
        """
        return [
            {
                'key': [('asset_project_id', 1)],
                'name': 'asset_project_id_idx',
                'unique': False,
            },
            {
                'key': [('asset_project_id', 1), ('asset_name', 1)],
                'name': 'asset_project_name_unique_idx',
                'unique': True,
            },
            {
                'key': [('asset_status', 1)],
                'name': 'asset_status_idx',
                'unique': False,
            },
            {
                'key': [('asset_type', 1)],
                'name': 'asset_type_idx',
                'unique': False,
            },
            {
                'key': [('source_uri', 1)],
                'name': 'asset_source_uri_idx',
                'unique': False,
            },
        ]