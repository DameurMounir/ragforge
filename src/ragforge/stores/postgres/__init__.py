"""
PostgreSQL persistence boundary for RAGForge.

This package intentionally stays separate from the existing MongoDB stores.
Branch 20 introduces PostgreSQL as a production-grade persistence option without
breaking the working Branch 19 RAG Core.
"""

from src.ragforge.stores.postgres.session import (
    PostgresConnectionSettings,
    PostgresSessionManager,
    build_postgres_async_url,
    build_postgres_sync_url,
)
from src.ragforge.stores.postgres.unit_of_work import PostgresUnitOfWork

__all__ = [
    'PostgresConnectionSettings',
    'PostgresSessionManager',
    'PostgresUnitOfWork',
    'build_postgres_async_url',
    'build_postgres_sync_url',
]
