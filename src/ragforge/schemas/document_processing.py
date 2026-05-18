from pydantic import BaseModel, Field, model_validator


class ProcessDocumentRequest(BaseModel):
    stored_filename: str = Field(..., min_length=1)
    chunk_size: int = Field(default=1000, gt=0)
    overlap_size: int = Field(default=200, ge=0)
    do_reset: bool = False

    @model_validator(mode='after')
    def validate_overlap_size(self):
        if self.overlap_size >= self.chunk_size:
            raise ValueError('overlap_size must be smaller than chunk_size')

        return self