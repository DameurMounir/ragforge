from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


@dataclass(frozen=True)
class PostgresConnectionSettings:
    """
    Primitive PostgreSQL connection values.

    This object deliberately does not depend on Pydantic settings. It can be
    built from the app settings, from environment variables, or from tests.
    Keeping it small makes Alembic, scripts, tests, and FastAPI startup share
    the same URL-building logic.
    """

    username: str
    password: str
    host: str
    port: int
    database: str

    @classmethod
    def from_settings(cls, settings: Any) -> 'PostgresConnectionSettings':
        """
        Build connection settings from the existing RAGForge settings object.
        """

        return cls(
            username=str(settings.POSTGRES_USER),
            password=str(settings.POSTGRES_PASSWORD),
            host=str(settings.POSTGRES_HOST),
            port=int(settings.POSTGRES_PORT),
            database=str(settings.POSTGRES_DB),
        )

    @classmethod
    def from_env(cls) -> 'PostgresConnectionSettings':
        """
        Build connection settings directly from environment variables.

        This path is used by validation scripts and Alembic when the full app
        settings object is not available.
        """

        return cls(
            username=os.getenv('POSTGRES_USER', 'ragforge'),
            password=os.getenv('POSTGRES_PASSWORD', 'ragforge_password_change_me'),
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=int(os.getenv('POSTGRES_PORT', '5433')),
            database=os.getenv('POSTGRES_DB', 'ragforge'),
        )


def _build_postgres_url(
    connection: PostgresConnectionSettings,
    driver: str,
) -> str:
    """
    Build a SQLAlchemy PostgreSQL URL safely.

    SQLAlchemy's URL object correctly escapes special characters in usernames,
    passwords, hosts, and database names. Avoid manual f-strings for database
    URLs because passwords often contain characters such as `@`, `/`, `#`, or `%`.
    """

    url = URL.create(
        drivername=f'postgresql+{driver}',
        username=connection.username,
        password=connection.password,
        host=connection.host,
        port=connection.port,
        database=connection.database,
    )
    return url.render_as_string(hide_password=False)


def build_postgres_async_url(connection: PostgresConnectionSettings) -> str:
    """
    Build the async SQLAlchemy URL used by FastAPI runtime.
    """

    return _build_postgres_url(connection=connection, driver='asyncpg')


def build_postgres_sync_url(connection: PostgresConnectionSettings) -> str:
    """
    Build the sync SQLAlchemy URL used by Alembic migrations.
    """

    return _build_postgres_url(connection=connection, driver='psycopg')


def escape_alembic_url(url: str) -> str:
    """
    Escape `%` characters before passing a URL to Alembic ConfigParser.

    Alembic configuration files use ConfigParser interpolation. A database URL
    containing `%` must be escaped as `%%` when set through config options.
    """

    return url.replace('%', '%%')


class PostgresSessionManager:
    """
    Owns the async SQLAlchemy engine and session factory.

    Responsibilities:
    - create and configure the async engine,
    - expose session factories to UnitOfWork objects,
    - provide health checks,
    - dispose the engine pool on shutdown.

    It does not perform business operations and it does not replace the service
    layer. It is infrastructure only.
    """

    def __init__(
        self,
        database_url: str,
        echo: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        pool_recycle: int = 1800,
    ) -> None:
        self.database_url = database_url
        self.engine: AsyncEngine = create_async_engine(
            database_url,
            echo=echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            pool_pre_ping=True,
        )
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

    @classmethod
    def from_settings(cls, settings: Any) -> 'PostgresSessionManager':
        """
        Create a manager directly from RAGForge settings.
        """

        connection = PostgresConnectionSettings.from_settings(settings)
        return cls(
            database_url=build_postgres_async_url(connection),
            echo=bool(getattr(settings, 'POSTGRES_ECHO', False)),
            pool_size=int(getattr(settings, 'POSTGRES_POOL_SIZE', 5)),
            max_overflow=int(getattr(settings, 'POSTGRES_MAX_OVERFLOW', 10)),
            pool_timeout=int(getattr(settings, 'POSTGRES_POOL_TIMEOUT', 30)),
            pool_recycle=int(getattr(settings, 'POSTGRES_POOL_RECYCLE', 1800)),
        )

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """
        Provide one isolated AsyncSession.

        This method does not commit. Transaction policy belongs to the Unit of
        Work or an explicit service transaction.
        """

        async with self.session_factory() as session:
            yield session

    async def ping(self) -> bool:
        """
        Validate that PostgreSQL is reachable.
        """

        async with self.session() as session:
            await session.execute(text('SELECT 1'))
        return True

    async def dispose(self) -> None:
        """
        Close the SQLAlchemy engine pool during application shutdown.
        """

        await self.engine.dispose()
