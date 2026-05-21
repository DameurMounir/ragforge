from typing import Optional

from bson.objectid import ObjectId
from pydantic import BaseModel, ConfigDict, Field


class DataChunk(BaseModel):
    """
    Database scheme representing a text chunk extracted from an asset.
    """

    id: Optional[ObjectId] = Field(default=None, alias='_id')

    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict = Field(default_factory=dict)

    chunk_order: int = Field(..., gt=0)

    chunk_project_id: ObjectId
    chunk_asset_id: ObjectId

    embedded: bool = False
    embedding_model: Optional[str] = None
    vector_id: Optional[str] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    @classmethod
    def get_indexes(cls) -> list[dict]:
        """
        Return MongoDB indexes required for the data_chunks collection./Branch 11

        These indexes prepare future semantic search and chunk retrieval.
        
        """
        return [
            {
                'key': [('chunk_project_id', 1)],
                'name': 'chunk_project_id_idx',
                'unique': False,
            },
            {
                'key': [('chunk_asset_id', 1)],
                'name': 'chunk_asset_id_idx',
                'unique': False,
            },
            {
                'key': [('chunk_project_id', 1), ('chunk_asset_id', 1)],
                'name': 'chunk_project_asset_idx',
                'unique': False,
            },
            {
                'key': [
                    ('chunk_project_id', 1),
                    ('chunk_asset_id', 1),
                    ('chunk_order', 1),
                ],
                'name': 'chunk_project_asset_order_unique_idx',
                'unique': True,
            },
            {
                'key': [('embedded', 1)],
                'name': 'chunk_embedded_idx',
                'unique': False,
            },
            {
                'key': [('vector_id', 1)],
                'name': 'chunk_vector_id_idx',
                'unique': False,
            },
        ]