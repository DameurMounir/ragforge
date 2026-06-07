from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

import pytest

from src.ragforge.providers.vector_db.implementations.pgvector_provider import (
    PgVectorProvider,
)


class DummySessionManager:
    """Session manager placeholder for unit tests that do not touch PostgreSQL."""

    async def dispose(self) -> None:
        return None


class CapturedResult:
    def __init__(self, scalar_value: int | None = None, rowcount: int = 0):
        self._scalar_value = scalar_value
        self.rowcount = rowcount

    def scalar_one(self):
        return self._scalar_value

    def scalar_one_or_none(self):
        return self._scalar_value

    def fetchall(self):
        return []

    def mappings(self):
        return self

    def one(self):
        return {
            'total_records': 0,
            'total_projects': 0,
            'total_assets': 0,
            'total_vector_sizes': 0,
        }

    def all(self):
        return []


class CapturedSession:
    def __init__(self, configured_record_count: int = 0):
        self.configured_record_count = configured_record_count
        self.executed: list[tuple[str, dict[str, Any] | None]] = []
        self.commit_count = 0

    async def execute(self, statement, params: dict[str, Any] | None = None):
        sql = str(statement)
        self.executed.append((sql, params))
        if 'SELECT COUNT(*)' in sql:
            return CapturedResult(scalar_value=self.configured_record_count)
        return CapturedResult(rowcount=0)

    async def commit(self) -> None:
        self.commit_count += 1


class CapturedSessionContext:
    def __init__(self, session: CapturedSession):
        self.session = session

    async def __aenter__(self) -> CapturedSession:
        return self.session

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        return False


class CapturingSessionManager:
    """Fake SQLAlchemy async session manager that captures SQL statements."""

    def __init__(self, configured_record_count: int = 0):
        self.session_obj = CapturedSession(
            configured_record_count=configured_record_count
        )
        self.dispose_count = 0

    def session(self) -> CapturedSessionContext:
        return CapturedSessionContext(self.session_obj)

    async def dispose(self) -> None:
        self.dispose_count += 1


class QdrantSettings:
    VECTOR_DB_PROVIDER = 'qdrant'
    QDRANT_MODE = 'local'
    QDRANT_URL = 'http://localhost:6333'
    QDRANT_API_KEY = None
    QDRANT_LOCAL_PATH = 'storage/vector_db/test_qdrant'
    QDRANT_PREFER_GRPC = False


class PgVectorSettings:
    VECTOR_DB_PROVIDER = 'pgvector'
    VECTOR_DB_DISTANCE = 'cosine'
    EMBEDDING_VECTOR_SIZE = 384
    EMBEDDING_MODEL = 'fake-embedding-model'
    EMBEDDING_PROVIDER = 'fake'
    VECTOR_DB_COLLECTION_NAME = 'ragforge_chunks'
    PGVECTOR_TABLE_NAME = 'vector_records'
    PGVECTOR_VECTOR_SIZE = None
    PGVECTOR_DISTANCE = 'cosine'
    PGVECTOR_INDEX_TYPE = 'hnsw'
    PGVECTOR_INDEX_VECTOR_TYPE = 'vector'
    PGVECTOR_HNSW_M = 16
    PGVECTOR_HNSW_EF_CONSTRUCTION = 64
    PGVECTOR_HNSW_EF_SEARCH = 40
    PGVECTOR_IVFFLAT_LISTS = 100
    PGVECTOR_IVFFLAT_PROBES = 10
    PGVECTOR_INDEX_MIN_RECORDS = 0
    PGVECTOR_AUTO_CREATE_INDEX = True
    PGVECTOR_CREATE_EXTENSION_ON_STARTUP = True
    POSTGRES_USER = 'ragforge'
    POSTGRES_PASSWORD = 'ragforge_password_change_me'
    POSTGRES_HOST = 'localhost'
    POSTGRES_PORT = 5433
    POSTGRES_DB = 'ragforge'
    POSTGRES_ECHO = False
    POSTGRES_POOL_SIZE = 5
    POSTGRES_MAX_OVERFLOW = 10
    POSTGRES_POOL_TIMEOUT = 30
    POSTGRES_POOL_RECYCLE = 1800

    @property
    def PGVECTOR_EFFECTIVE_VECTOR_SIZE(self) -> int:
        if self.PGVECTOR_VECTOR_SIZE is None:
            return int(self.EMBEDDING_VECTOR_SIZE)
        if int(self.PGVECTOR_VECTOR_SIZE) != int(self.EMBEDDING_VECTOR_SIZE):
            raise ValueError('PGVECTOR_VECTOR_SIZE must match EMBEDDING_VECTOR_SIZE.')
        return int(self.PGVECTOR_VECTOR_SIZE)


class PgVectorExplicitSizeSettings(PgVectorSettings):
    PGVECTOR_VECTOR_SIZE = 384


class ConflictingPgVectorSettings(PgVectorSettings):
    PGVECTOR_VECTOR_SIZE = 768


class IncompletePgVectorSettings:
    VECTOR_DB_PROVIDER = 'pgvector'
    EMBEDDING_VECTOR_SIZE = 384
    EMBEDDING_MODEL = 'fake-embedding-model'
    EMBEDDING_PROVIDER = 'fake'
    PGVECTOR_TABLE_NAME = 'vector_records'
    PGVECTOR_EFFECTIVE_VECTOR_SIZE = 384
    PGVECTOR_DISTANCE = 'cosine'
    # PGVECTOR_INDEX_TYPE is intentionally missing.
    PGVECTOR_INDEX_VECTOR_TYPE = 'vector'
    PGVECTOR_HNSW_M = 16
    PGVECTOR_HNSW_EF_CONSTRUCTION = 64
    PGVECTOR_HNSW_EF_SEARCH = 40
    PGVECTOR_IVFFLAT_LISTS = 100
    PGVECTOR_IVFFLAT_PROBES = 10
    PGVECTOR_INDEX_MIN_RECORDS = 0
    PGVECTOR_AUTO_CREATE_INDEX = True
    PGVECTOR_CREATE_EXTENSION_ON_STARTUP = True
    POSTGRES_USER = 'ragforge'
    POSTGRES_PASSWORD = 'ragforge_password_change_me'
    POSTGRES_HOST = 'localhost'
    POSTGRES_PORT = 5433
    POSTGRES_DB = 'ragforge'
    POSTGRES_ECHO = False
    POSTGRES_POOL_SIZE = 5
    POSTGRES_MAX_OVERFLOW = 10
    POSTGRES_POOL_TIMEOUT = 30
    POSTGRES_POOL_RECYCLE = 1800


class BadProviderSettings:
    VECTOR_DB_PROVIDER = 'unknown_provider'


@pytest.fixture
def dummy_session_manager() -> DummySessionManager:
    return DummySessionManager()


@pytest.fixture
def capturing_session_manager() -> CapturingSessionManager:
    return CapturingSessionManager(configured_record_count=0)


@pytest.fixture
def pgvector_settings() -> PgVectorSettings:
    return PgVectorSettings()


@pytest.fixture
def make_pgvector_provider(dummy_session_manager):
    def _make(**kwargs):
        defaults = {
            'session_manager': dummy_session_manager,
            'table_name': 'vector_records',
            'vector_size': 384,
            'distance': 'cosine',
            'index_type': 'hnsw',
            'index_vector_type': 'vector',
            'hnsw_m': 16,
            'hnsw_ef_construction': 64,
            'hnsw_ef_search': 40,
            'ivfflat_lists': 100,
            'ivfflat_probes': 10,
            'index_min_records': 0,
            'auto_create_index': True,
            'create_extension_on_startup': True,
            'embedding_model': 'fake-embedding-model',
            'embedding_provider': 'fake',
        }
        defaults.update(kwargs)
        return PgVectorProvider(**defaults)

    return _make


@pytest.fixture
def make_capturing_pgvector_provider():
    def _make(
        configured_record_count: int = 0,
        **kwargs,
    ):
        session_manager = CapturingSessionManager(
            configured_record_count=configured_record_count
        )
        defaults = {
            'session_manager': session_manager,
            'table_name': 'vector_records',
            'vector_size': 384,
            'distance': 'cosine',
            'index_type': 'hnsw',
            'index_vector_type': 'vector',
            'hnsw_m': 16,
            'hnsw_ef_construction': 64,
            'hnsw_ef_search': 40,
            'ivfflat_lists': 100,
            'ivfflat_probes': 10,
            'index_min_records': 0,
            'auto_create_index': True,
            'create_extension_on_startup': True,
            'embedding_model': 'fake-embedding-model',
            'embedding_provider': 'fake',
        }
        defaults.update(kwargs)
        provider = PgVectorProvider(**defaults)
        return provider, session_manager

    return _make


@pytest.fixture
def sample_vector_record():
    from src.ragforge.providers.vector_db.schemas import VectorRecord

    return VectorRecord(
        record_id='chunk-001',
        vector=[0.1, 0.2, 0.3, 0.4],
        text='Branch 21 PgVector test text.',
        metadata={
            'project_id': 'project-db-id',
            'asset_id': 'asset-db-id',
            'chunk_id': 'chunk-001',
            'chunk_order': 1,
            'embedding_model': 'fake-embedding-model',
            'embedding_provider': 'fake',
        },
    )
