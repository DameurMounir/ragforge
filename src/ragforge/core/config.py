# Import lru_cache to cache the settings object.
# This prevents creating a new Settings instance every time get_settings() is called.
from functools import lru_cache

# BaseSettings is used to load configuration values from environment variables
# or from a .env file.
# SettingsConfigDict is used in Pydantic v2 to configure how settings are loaded.
from pydantic_settings import BaseSettings, SettingsConfigDict


# This class represents the global application configuration.
# Each attribute here must exist in the .env file unless we give it a default value.
class Settings(BaseSettings):
    # Application name.
    # Example in .env:
    # APP_NAME="RAGForge"
    APP_NAME: str

    # Application version.
    # Example in .env:
    # APP_VERSION="0.1.0"
    APP_VERSION: str

    # Application environment.
    # Example in .env:
    # APP_ENV="development"
    APP_ENV: str

    # Maximum accepted upload file size in megabytes.
    # Example in .env:
    # FILE_MAX_SIZE_MB=10
    FILE_MAX_SIZE_MB: int

    # Allowed file extensions.
    # This checks the filename extension, such as pdf, txt, or docx.
    # Example in .env:
    # FILE_ALLOWED_EXTENSIONS=["pdf", "txt", "docx"]
    FILE_ALLOWED_EXTENSIONS: list[str]

    # Allowed MIME types.
    # This checks the file content type sent by the client/browser.
    # Example in .env:
    # FILE_ALLOWED_MIME_TYPES=["application/pdf", "text/plain"]
    FILE_ALLOWED_MIME_TYPES: list[str]

    # Storage settings // added at milestone 3 branche 6
    UPLOAD_DIR: str = 'storage/uploads'
    PROJECT_DOCUMENTS_DIR: str = 'documents'
    # Pydantic v2 configuration.
    # This tells Pydantic to read values from the .env file.
    model_config = SettingsConfigDict(
        # Name of the environment file.
        env_file='.env',

        # Encoding used to read the .env file.
        env_file_encoding='utf-8',

        # Ignore extra variables in .env that are not declared in this class.
        # Example: OPENAI_API_KEY can exist in .env even if it is not declared above.
        extra='ignore'
    )


# Cache the settings object after the first call.
# Without this, every call to get_settings() creates a new Settings() object.
@lru_cache
def get_settings() -> Settings:
    # Create and return one Settings instance loaded from .env.
    return Settings()