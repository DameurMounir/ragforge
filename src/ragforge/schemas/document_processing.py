from pydantic import BaseModel, Field, model_validator


class ProcessDocumentRequest(BaseModel):
    """
    Request body for document processing.

    Branch 13 behavior:
    - asset_id provided        -> process one asset by MongoDB id
    - stored_filename provided -> process one asset by stored filename
    - none provided            -> process all FILE assets in the project
    """

    asset_id: str | None = Field(default=None, min_length=1)
    stored_filename: str | None = Field(default=None, min_length=1)

    chunk_size: int = Field(default=1000, gt=0)
    overlap_size: int = Field(default=200, ge=0)

    do_reset: bool = False
    include_chunks: bool = False

    @model_validator(mode='after')
    def validate_processing_request(self):
        if self.asset_id and self.stored_filename:
            raise ValueError(
                'Use either asset_id or stored_filename, not both.'
            )

        if self.overlap_size >= self.chunk_size:
            raise ValueError(
                'overlap_size must be smaller than chunk_size'
            )

        return self
    