from __future__ import annotations

from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.ragforge.stores.postgres.repositories.asset_repository import (
    PostgresAssetRepository,
)
from src.ragforge.stores.postgres.repositories.chunk_repository import (
    PostgresChunkRepository,
)
from src.ragforge.stores.postgres.repositories.project_repository import (
    PostgresProjectRepository,
)


class PostgresUnitOfWorkError(RuntimeError):
    """Raised when a Unit of Work is used outside its valid transaction lifecycle."""


class PostgresUnitOfWork:
    """
    Transaction boundary for PostgreSQL operations.

    One UnitOfWork equals one transaction. Repositories share the same session
    and never commit by themselves. This enables atomic flows such as:

    - get or create project,
    - create/update asset,
    - replace chunks,
    - update processing status,
    - commit once.

    If any step fails, the whole transaction is rolled back.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory
        self.session: AsyncSession | None = None
        self.projects: PostgresProjectRepository | None = None
        self.assets: PostgresAssetRepository | None = None
        self.chunks: PostgresChunkRepository | None = None
        self._committed = False
        self._closed = False

    async def __aenter__(self) -> 'PostgresUnitOfWork':
        if self.session is not None or self._closed:
            raise PostgresUnitOfWorkError('This UnitOfWork instance cannot be reused.')

        self.session = self.session_factory()
        self.projects = PostgresProjectRepository(self.session)
        self.assets = PostgresAssetRepository(self.session)
        self.chunks = PostgresChunkRepository(self.session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self.session is None:
            self._closed = True
            return

        try:
            if exc_type is not None or not self._committed:
                await self.session.rollback()
        finally:
            await self.session.close()
            self._detach_repositories()
            self._closed = True

    def _require_active_session(self) -> AsyncSession:
        if self.session is None or self._closed:
            raise PostgresUnitOfWorkError('PostgresUnitOfWork is not active.')
        if self._committed:
            raise PostgresUnitOfWorkError('PostgresUnitOfWork has already been committed.')
        return self.session

    def _detach_repositories(self) -> None:
        self.session = None
        self.projects = None
        self.assets = None
        self.chunks = None

    async def commit(self) -> None:
        """
        Commit the active transaction exactly once.

        After commit, repositories are detached to prevent accidental writes
        after the transaction has ended.
        """

        session = self._require_active_session()
        await session.commit()
        self._committed = True
        await session.close()
        self._detach_repositories()
        self._closed = True

    async def rollback(self) -> None:
        """
        Explicitly roll back and close the active transaction.
        """

        session = self._require_active_session()
        await session.rollback()
        await session.close()
        self._detach_repositories()
        self._closed = True
