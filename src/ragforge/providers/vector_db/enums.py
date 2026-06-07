from enum import Enum


class VectorDBProvider(str, Enum):
    """Supported vector database providers."""

    QDRANT = 'qdrant'
    PGVECTOR = 'pgvector'


class QdrantMode(str, Enum):
    """Qdrant execution modes."""

    SERVER = 'server'
    LOCAL = 'local'


class DistanceMethod(str, Enum):
    """Provider-neutral vector distance methods."""

    COSINE = 'cosine'
    DOT = 'dot'
    EUCLID = 'euclid'


class PgVectorIndexType(str, Enum):
    """PgVector approximate nearest-neighbor index types."""

    HNSW = 'hnsw'
    IVFFLAT = 'ivfflat'


class PgVectorIndexVectorType(str, Enum):
    """PgVector index expression storage type."""

    VECTOR = 'vector'
    HALFVEC = 'halfvec'


class PgVectorColumn(str, Enum):
    """Stable column names for the Alembic-managed vector_records table."""

    ID = 'id'
    VECTOR_RECORD_UUID = 'vector_record_uuid'
    COLLECTION_NAME = 'collection_name'
    RECORD_ID = 'record_id'
    TEXT = 'text'
    EMBEDDING = 'embedding'
    VECTOR_SIZE = 'vector_size'
    EMBEDDING_MODEL = 'embedding_model'
    EMBEDDING_PROVIDER = 'embedding_provider'
    PROJECT_ID = 'project_id'
    ASSET_ID = 'asset_id'
    CHUNK_ID = 'chunk_id'
    CHUNK_ORDER = 'chunk_order'
    METADATA = 'metadata'
    CREATED_AT = 'created_at'
    UPDATED_AT = 'updated_at'
