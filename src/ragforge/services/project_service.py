import re
from pathlib import Path

from src.ragforge.services.base_service import BaseService


class ProjectService(BaseService):
    """
    Service responsible for project-based storage folders.

    Storage structure:
    storage/uploads/{project_id}/documents/
    """

    def __init__(self):
        super().__init__()

    def validate_project_id(self, project_id: str) -> str:
        """
        Validate project_id before using it as a folder name.

        Allowed characters:
        - letters
        - numbers
        - underscore _
        - hyphen -
        """
        if not project_id:
            raise ValueError('Project id is required')

        project_id = project_id.strip()

        if not project_id:
            raise ValueError('Project id is required')

        if not re.match(r'^[a-zA-Z0-9_-]+$', project_id):
            raise ValueError('Invalid project_id')

        return project_id

    def get_project_upload_dir(self, project_id: str) -> Path:
        """
        Return the base upload folder for a project.

        Example:
        storage/uploads/project_001
        """
        safe_project_id = self.validate_project_id(project_id)
        return self.uploads_dir / safe_project_id

    def get_project_documents_dir(self, project_id: str) -> Path:
        """
        Return the documents folder for a project.

        Example:
        storage/uploads/project_001/documents
        """
        project_upload_dir = self.get_project_upload_dir(project_id)
        return project_upload_dir / self.settings.PROJECT_DOCUMENTS_DIR

    def create_project_storage(self, project_id: str) -> Path:
        """
        Create project storage folders if they do not exist.

        Final structure:
        storage/uploads/{project_id}/documents/
        """
        project_documents_dir = self.get_project_documents_dir(project_id)
        return self.ensure_directory(project_documents_dir)

    def get_or_create_project_documents_dir(self, project_id: str) -> Path:
        """
        Return the project documents directory.

        If the directory does not exist, create it first.

        This method is used by DocumentService before saving uploaded files.
        """
        return self.create_project_storage(project_id)
        