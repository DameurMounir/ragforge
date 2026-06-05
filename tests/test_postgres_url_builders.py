from __future__ import annotations

from src.ragforge.stores.postgres.session import (
    PostgresConnectionSettings,
    build_postgres_async_url,
    build_postgres_sync_url,
    escape_alembic_url,
)


def test_postgres_url_builders_escape_special_password_characters() -> None:
    connection = PostgresConnectionSettings(
        username='ragforge',
        password='p@ss/word#with%chars',
        host='localhost',
        port=5433,
        database='ragforge',
    )

    async_url = build_postgres_async_url(connection)
    sync_url = build_postgres_sync_url(connection)

    assert async_url.startswith('postgresql+asyncpg://')
    assert sync_url.startswith('postgresql+psycopg://')
    assert 'p%40ss%2Fword%23with%25chars' in async_url
    assert 'p%40ss%2Fword%23with%25chars' in sync_url
    assert '%%25' in escape_alembic_url(sync_url)
