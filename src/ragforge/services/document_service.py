import re
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from src.ragforge.models import ResponseSignal
from src.ragforge.services.base_service import BaseService
from src.ragforge.services.project_service import ProjectService


class DocumentService(BaseService):
    """
    Service responsible for document validation and file path generation.

    This service prepares the uploaded document before the route writes it
    to disk with aiofiles.
    """

    def __init__(self):
        super().__init__()
        self.size_scale = 1024 * 1024
        self.project_service = ProjectService()

    def validate_uploaded_file(self, file: UploadFile):
        """
        Validate uploaded file MIME type and size.
        """
        if file.content_type not in self.settings.FILE_ALLOWED_MIME_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value

        if file.size and file.size > self.settings.FILE_MAX_SIZE_MB * self.size_scale:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value

        return True, ResponseSignal.FILE_VALIDATION_SUCCESS.value

    def get_clean_file_name(self, original_filename: str) -> str:
        """
        Clean the original filename before storing it.

        This removes dangerous path parts and unsafe characters.
        """
        filename = Path(original_filename).name
        filename = filename.strip().replace(' ', '_')
        filename = re.sub(r'[^\w.-]', '', filename)

        if not filename:
            filename = 'uploaded_file'

        return filename

    def generate_unique_file_path(self, original_filename: str, project_id: str):
        """
        Generate a unique document id, stored filename, and storage path.

        Final structure:
        storage/uploads/{project_id}/documents/{document_id}_{filename}
        """
        project_documents_dir = (
            self.project_service.get_or_create_project_documents_dir(
                project_id=project_id
            )
        )

        clean_filename = self.get_clean_file_name(
            original_filename=original_filename
        )

        document_id = str(uuid4())
        stored_filename = f'{document_id}_{clean_filename}'
        file_path = project_documents_dir / stored_filename

        while file_path.exists():
            document_id = str(uuid4())
            stored_filename = f'{document_id}_{clean_filename}'
            file_path = project_documents_dir / stored_filename

        return file_path, document_id, stored_filename