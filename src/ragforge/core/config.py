# Import lru_cache to cache the settings object.
# This prevents creating a new Settings instance every time get_settings() is called.
from functools import lru_cache

# BaseSettings is used to load configuration values from environment variables
# or from a .env file.
# SettingsConfigDict is used in Pydantic v2 to configure how settings are loaded.
from pydantic_settings import BaseSettings, SettingsConfigDict


# This class represents the global application configuration.
# Each attribute here can be loaded from the .env file.
# If an attribute has a default value, the app can run even if it is missing from .env.
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
    # Default value: 10 MB.
    FILE_MAX_SIZE_MB: int = 20

    # Default chunk size used when reading or saving uploaded files.
    # 1024 * 1024 = 1 MB per chunk.
    FILE_DEFAULT_CHUNK_SIZE: int = 1024 * 1024

    # Allowed file extensions.
    # This checks the filename extension, such as pdf, txt, or docx.
    FILE_ALLOWED_EXTENSIONS: list[str] = ['pdf', 'txt', 'docx']

    # Allowed MIME types.
    # This checks the file content type sent by the client/browser.
    FILE_ALLOWED_MIME_TYPES: list[str] = [
        'application/pdf',
        'text/plain',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]
    
    #Branch 11 /auth
    MONGO_INITDB_ROOT_USERNAME: str
    MONGO_INITDB_ROOT_PASSWORD: str

    MONGODB_DATABASE: str
    MONGODB_URL: str

    #################

        # LLM provider settings.
    LLM_PROVIDER: str = 'fake'
    LLM_DEFAULT_MODEL: str = 'fake-ragforge-model'
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_OUTPUT_TOKENS: int = 512
    LLM_TIMEOUT_SECONDS: int = 60

    # OpenAI-compatible provider settings.
    OPENAI_API_KEY: str | None = None
    OPENAI_BASE_URL: str | None = None

        # Vector DB provider settings.
    VECTOR_DB_PROVIDER: str = 'qdrant'

    # Qdrant settings.
    # server = connect to Docker/server Qdrant through QDRANT_URL.
    # local = embedded Qdrant stored in QDRANT_LOCAL_PATH.
    QDRANT_MODE: str = 'server'
    QDRANT_URL: str = 'http://localhost:6333'
    QDRANT_API_KEY: str | None = None
    QDRANT_LOCAL_PATH: str = 'storage/vector_db/qdrant'

    QDRANT_COLLECTION_NAME: str = 'ragforge_chunks'
    QDRANT_VECTOR_SIZE: int = 1536
    QDRANT_DISTANCE: str = 'cosine'
    QDRANT_PREFER_GRPC: bool = False


    #embedding 
    EMBEDDING_PROVIDER: str = 'fake'
    EMBEDDING_MODEL: str = 'text-embedding-3-small'
    EMBEDDING_VECTOR_SIZE: int = 1536
    EMBEDDING_BATCH_SIZE: int = 32
    FAKE_EMBEDDING_MODEL: str = 'fake-embedding-model'

    EMBEDDING_OPENAI_API_KEY: str | None = None
    EMBEDDING_OPENAI_BASE_URL: str | None = None


    # Generic vector indexing settings.
    VECTOR_DB_COLLECTION_NAME: str = 'ragforge_chunks'
    VECTOR_DB_VECTOR_SIZE: int = 1536
    VECTOR_DB_DISTANCE: str = 'cosine'

    # Semantic search settings.
    SEARCH_DEFAULT_LIMIT: int = 5
    SEARCH_MAX_LIMIT: int = 20
    SEARCH_MIN_SCORE: float | None = None
    SEARCH_INCLUDE_TEXT_DEFAULT: bool = True
    SEARCH_INCLUDE_METADATA_DEFAULT: bool = True

    # Branch 18 grounded answer settings.
    RAG_ANSWER_DEFAULT_LIMIT: int = 5
    RAG_ANSWER_MAX_CONTEXT_CHARS: int = 8000
    RAG_ANSWER_INCLUDE_SOURCES_DEFAULT: bool = True
    RAG_ANSWER_INCLUDE_EVIDENCE_DEFAULT: bool = True
    RAG_ANSWER_DEBUG_PROMPT_DEFAULT: bool = False

    # Branch 19 retrieval quality and citation stability settings.
    RAG_RETRIEVAL_CANDIDATE_LIMIT: int = 30
    RAG_RETRIEVAL_MIN_SCORE: float | None = 0.25
    RAG_MAX_CHUNKS_PER_ASSET: int = 3
    RAG_ENABLE_SOURCE_DEDUP: bool = True
    RAG_ENABLE_DOMINANT_ASSET: bool = True
    RAG_DOMINANT_ASSET_SCORE_GAP: float = 0.08
    RAG_DOMINANT_ASSET_MIN_CHUNKS: int = 2
    RAG_ENABLE_CITATION_VALIDATION: bool = True

    # Root upload directory.
    # All uploaded files will be stored inside this folder.
    UPLOAD_DIR: str = 'storage/uploads'

    # Subdirectory used inside each project folder to store documents.
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

