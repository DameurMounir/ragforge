from pathlib import Path

from src.ragforge.core.config import get_settings


class BaseService:
    """
    Base service for shared settings and common storage helpers.
    """

    def __init__(self):
        self.settings = get_settings()
        self.uploads_dir = Path(self.settings.UPLOAD_DIR)

    def ensure_directory(self, directory_path: Path) -> Path:
        """
        Create a directory if it does not exist and return it.
        """
        directory_path.mkdir(parents=True, exist_ok=True)
        return directory_path