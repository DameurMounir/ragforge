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
        """
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
        """
        project_documents_dir = self.get_project_documents_dir(project_id)
        return self.ensure_directory(project_documents_dir)