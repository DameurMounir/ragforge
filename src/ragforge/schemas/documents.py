from datetime import datetime

from pydantic import BaseModel, Field


class UploadDocumentResponse(BaseModel):
    signal: str
    message: str
    document_id: str
    asset_id: str
    project_id: str
    original_filename: str
    stored_filename: str
    content_type: str | None
    file_size: int = Field(ge=0)
    uploaded_at: datetime
