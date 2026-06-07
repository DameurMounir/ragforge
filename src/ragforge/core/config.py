# Import lru_cache to cache the settings object.
# This prevents creating a new Settings instance every time get_settings() is called.
from functools import lru_cache

# BaseSettings is used to load configuration values from environment variables
# or from a .env file.
# SettingsConfigDict is used in Pydantic v2 to configure how settings are loaded.
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Global RAGForge application configuration.

    Branch 21 policy:
    - Runtime behavior is configured through .env / environment variables.
    - Provider/factory code must not contain fallback defaults.
    - EMBEDDING_VECTOR_SIZE is the source of truth for vector dimensions.
    - QDRANT_VECTOR_SIZE, VECTOR_DB_VECTOR_SIZE, and PGVECTOR_VECTOR_SIZE are
      optional equality guards only. If set, they must match EMBEDDING_VECTOR_SIZE.
    """

    # Application settings.
    APP_NAME: str
    APP_VERSION: str
    APP_ENV: str

    # Upload and file validation settings.
    FILE_MAX_SIZE_MB: int = 20
    FILE_DEFAULT_CHUNK_SIZE: int = 1024 * 1024
    FILE_ALLOWED_EXTENSIONS: list[str] = ['pdf', 'txt', 'docx']
    FILE_ALLOWED_MIME_TYPES: list[str] = [
        'application/pdf',
        'text/plain',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    ]

    # Branch 11 / MongoDB auth and metadata persistence settings.
    MONGO_INITDB_ROOT_USERNAME: str
    MONGO_INITDB_ROOT_PASSWORD: str
    MONGODB_DATABASE: str
    MONGODB_URL: str

    # LLM provider settings.
    LLM_PROVIDER: str = 'fake'
    LLM_DEFAULT_MODEL: str = 'fake-ragforge-model'
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_OUTPUT_TOKENS: int = 512
    LLM_TIMEOUT_SECONDS: int = 60

    # OpenAI-compatible LLM provider settings.
    OPENAI_API_KEY: str | None = None
    OPENAI_BASE_URL: str | None = None

    # Vector DB provider settings.
    VECTOR_DB_PROVIDER: str = 'qdrant'

    # Qdrant settings.
    # QDRANT_VECTOR_SIZE is optional and acts only as an equality guard.
    # The effective vector size is always resolved from EMBEDDING_VECTOR_SIZE.
    QDRANT_MODE: str = 'server'
    QDRANT_URL: str = 'http://localhost:6333'
    QDRANT_API_KEY: str | None = None
    QDRANT_LOCAL_PATH: str = 'storage/vector_db/qdrant'
    QDRANT_COLLECTION_NAME: str = 'ragforge_chunks'
    QDRANT_VECTOR_SIZE: int | None = None
    QDRANT_DISTANCE: str = 'cosine'
    QDRANT_PREFER_GRPC: bool = False

    # Embedding provider settings.
    # EMBEDDING_VECTOR_SIZE is required because it is the source of truth for
    # Qdrant and PgVector dimensions. Do not hardcode model dimensions in code.
    EMBEDDING_PROVIDER: str = 'fake'
    EMBEDDING_MODEL: str = 'fake-embedding-model'
    EMBEDDING_VECTOR_SIZE: int
    EMBEDDING_BATCH_SIZE: int = 32
    FAKE_EMBEDDING_MODEL: str = 'fake-embedding-model'

    EMBEDDING_OPENAI_API_KEY: str | None = None
    EMBEDDING_OPENAI_BASE_URL: str | None = None

    # Generic vector indexing settings.
    # VECTOR_DB_VECTOR_SIZE is optional and acts only as an equality guard.
    VECTOR_DB_COLLECTION_NAME: str = 'ragforge_chunks'
    VECTOR_DB_VECTOR_SIZE: int | None = None
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

    # Branch 20 — PostgreSQL + SQLAlchemy + Alembic Production Persistence Layer.
    POSTGRES_USER: str = 'ragforge'
    POSTGRES_PASSWORD: str = 'ragforge_password_change_me'
    POSTGRES_HOST: str = 'localhost'
    POSTGRES_PORT: int = 5433
    POSTGRES_DB: str = 'ragforge'
    POSTGRES_ECHO: bool = False
    POSTGRES_POOL_SIZE: int = 5
    POSTGRES_MAX_OVERFLOW: int = 10
    POSTGRES_POOL_TIMEOUT: int = 30
    POSTGRES_POOL_RECYCLE: int = 1800

    # Branch 21 — PgVector provider settings.
    # No embedding model or vector dimension is hardcoded in provider/factory code.
    # PGVECTOR_VECTOR_SIZE is optional and must match EMBEDDING_VECTOR_SIZE when set.
    PGVECTOR_TABLE_NAME: str = 'vector_records'
    PGVECTOR_VECTOR_SIZE: int | None = None
    PGVECTOR_DISTANCE: str = 'cosine'
    PGVECTOR_INDEX_TYPE: str = 'hnsw'
    PGVECTOR_INDEX_VECTOR_TYPE: str = 'vector'
    PGVECTOR_HNSW_M: int = 16
    PGVECTOR_HNSW_EF_CONSTRUCTION: int = 64
    PGVECTOR_HNSW_EF_SEARCH: int = 40
    PGVECTOR_IVFFLAT_LISTS: int = 100
    PGVECTOR_IVFFLAT_PROBES: int = 10
    PGVECTOR_INDEX_MIN_RECORDS: int = 0
    PGVECTOR_AUTO_CREATE_INDEX: bool = True
    PGVECTOR_CREATE_EXTENSION_ON_STARTUP: bool = True

    # Storage settings.
    UPLOAD_DIR: str = 'storage/uploads'
    PROJECT_DOCUMENTS_DIR: str = 'documents'

    @property
    def VECTOR_DB_EFFECTIVE_VECTOR_SIZE(self) -> int:
        """
        Effective generic vector dimension used by vector DB services.

        RAGForge policy:
        - EMBEDDING_VECTOR_SIZE is the source of truth.
        - VECTOR_DB_VECTOR_SIZE is optional.
        - If VECTOR_DB_VECTOR_SIZE is set, it must equal EMBEDDING_VECTOR_SIZE.
        """
        return self._resolve_optional_vector_size_guard(
            guard_name='VECTOR_DB_VECTOR_SIZE',
            guard_value=self.VECTOR_DB_VECTOR_SIZE,
        )

    @property
    def QDRANT_EFFECTIVE_VECTOR_SIZE(self) -> int:
        """
        Effective Qdrant vector dimension.

        RAGForge policy:
        - EMBEDDING_VECTOR_SIZE is the source of truth.
        - QDRANT_VECTOR_SIZE is optional.
        - If QDRANT_VECTOR_SIZE is set, it must equal EMBEDDING_VECTOR_SIZE.
        """
        return self._resolve_optional_vector_size_guard(
            guard_name='QDRANT_VECTOR_SIZE',
            guard_value=self.QDRANT_VECTOR_SIZE,
        )

    @property
    def PGVECTOR_EFFECTIVE_VECTOR_SIZE(self) -> int:
        """
        Effective PgVector dimension used by the PgVector provider.

        RAGForge policy:
        - EMBEDDING_VECTOR_SIZE is the source of truth.
        - PGVECTOR_VECTOR_SIZE is optional.
        - If PGVECTOR_VECTOR_SIZE is set, it must equal EMBEDDING_VECTOR_SIZE.
        """
        return self._resolve_optional_vector_size_guard(
            guard_name='PGVECTOR_VECTOR_SIZE',
            guard_value=self.PGVECTOR_VECTOR_SIZE,
        )

    def _resolve_optional_vector_size_guard(
        self,
        guard_name: str,
        guard_value: int | None,
    ) -> int:
        """
        Return EMBEDDING_VECTOR_SIZE after validating an optional vector-size guard.
        """
        embedding_vector_size = int(self.EMBEDDING_VECTOR_SIZE)

        if embedding_vector_size <= 0:
            raise ValueError('EMBEDDING_VECTOR_SIZE must be greater than zero.')

        if guard_value is None:
            return embedding_vector_size

        if int(guard_value) != embedding_vector_size:
            raise ValueError(
                f'{guard_name} must match EMBEDDING_VECTOR_SIZE. '
                f'Got {guard_name}={guard_value} and '
                f'EMBEDDING_VECTOR_SIZE={embedding_vector_size}.'
            )

        return embedding_vector_size

    @model_validator(mode='after')
    def validate_branch_21_vector_settings(self):
        """
        Validate Branch 21 vector configuration once when Settings is created.

        This prevents hidden fallback behavior in factories/providers and fails fast
        if .env contains inconsistent vector dimensions or unsupported PgVector modes.
        """
        # Validate optional vector-size guards at settings construction time.
        _ = self.VECTOR_DB_EFFECTIVE_VECTOR_SIZE
        _ = self.QDRANT_EFFECTIVE_VECTOR_SIZE
        _ = self.PGVECTOR_EFFECTIVE_VECTOR_SIZE

        # Normalize string settings centrally so factories/providers do not need
        # fallback/default logic.
        self.VECTOR_DB_PROVIDER = self.VECTOR_DB_PROVIDER.lower().strip()
        self.QDRANT_DISTANCE = self.QDRANT_DISTANCE.lower().strip()
        self.VECTOR_DB_DISTANCE = self.VECTOR_DB_DISTANCE.lower().strip()
        self.PGVECTOR_DISTANCE = self.PGVECTOR_DISTANCE.lower().strip()
        self.PGVECTOR_INDEX_TYPE = self.PGVECTOR_INDEX_TYPE.lower().strip()
        self.PGVECTOR_INDEX_VECTOR_TYPE = (
            self.PGVECTOR_INDEX_VECTOR_TYPE.lower().strip()
        )

        allowed_vector_db_providers = {'qdrant', 'pgvector'}
        if self.VECTOR_DB_PROVIDER not in allowed_vector_db_providers:
            raise ValueError(
                'VECTOR_DB_PROVIDER must be one of: '
                f'{sorted(allowed_vector_db_providers)}. '
                f'Got {self.VECTOR_DB_PROVIDER!r}.'
            )

        allowed_distances = {'cosine', 'euclid', 'dot'}
        if self.PGVECTOR_DISTANCE not in allowed_distances:
            raise ValueError(
                'PGVECTOR_DISTANCE must be one of: '
                f'{sorted(allowed_distances)}. '
                f'Got {self.PGVECTOR_DISTANCE!r}.'
            )

        if self.QDRANT_DISTANCE not in allowed_distances:
            raise ValueError(
                'QDRANT_DISTANCE must be one of: '
                f'{sorted(allowed_distances)}. '
                f'Got {self.QDRANT_DISTANCE!r}.'
            )

        if self.VECTOR_DB_DISTANCE not in allowed_distances:
            raise ValueError(
                'VECTOR_DB_DISTANCE must be one of: '
                f'{sorted(allowed_distances)}. '
                f'Got {self.VECTOR_DB_DISTANCE!r}.'
            )

        allowed_pgvector_index_types = {'hnsw', 'ivfflat'}
        if self.PGVECTOR_INDEX_TYPE not in allowed_pgvector_index_types:
            raise ValueError(
                'PGVECTOR_INDEX_TYPE must be one of: '
                f'{sorted(allowed_pgvector_index_types)}. '
                f'Got {self.PGVECTOR_INDEX_TYPE!r}.'
            )

        allowed_pgvector_index_vector_types = {'vector', 'halfvec'}
        if self.PGVECTOR_INDEX_VECTOR_TYPE not in allowed_pgvector_index_vector_types:
            raise ValueError(
                'PGVECTOR_INDEX_VECTOR_TYPE must be one of: '
                f'{sorted(allowed_pgvector_index_vector_types)}. '
                f'Got {self.PGVECTOR_INDEX_VECTOR_TYPE!r}.'
            )

        if self.PGVECTOR_HNSW_M <= 0:
            raise ValueError('PGVECTOR_HNSW_M must be greater than zero.')

        if self.PGVECTOR_HNSW_EF_CONSTRUCTION <= 0:
            raise ValueError(
                'PGVECTOR_HNSW_EF_CONSTRUCTION must be greater than zero.'
            )

        if self.PGVECTOR_HNSW_EF_SEARCH <= 0:
            raise ValueError('PGVECTOR_HNSW_EF_SEARCH must be greater than zero.')

        if self.PGVECTOR_IVFFLAT_LISTS <= 0:
            raise ValueError('PGVECTOR_IVFFLAT_LISTS must be greater than zero.')

        if self.PGVECTOR_IVFFLAT_PROBES <= 0:
            raise ValueError('PGVECTOR_IVFFLAT_PROBES must be greater than zero.')

        if self.PGVECTOR_INDEX_MIN_RECORDS < 0:
            raise ValueError('PGVECTOR_INDEX_MIN_RECORDS must be >= 0.')

        return self

    # Pydantic v2 configuration.
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )


@lru_cache
def get_settings() -> Settings:
    """
    Create and return one cached Settings instance loaded from .env.
    """
    return Settings()
