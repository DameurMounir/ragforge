from __future__ import annotations

import inspect

from src.ragforge.stores.postgres.unit_of_work import PostgresUnitOfWork


def test_unit_of_work_owns_commit_and_rollback() -> None:
    source = inspect.getsource(PostgresUnitOfWork)

    assert 'async def commit' in source
    assert 'async def rollback' in source
    assert 'await session.commit()' in source
    assert 'await session.rollback()' in source


def test_unit_of_work_detaches_repositories_after_commit() -> None:
    source = inspect.getsource(PostgresUnitOfWork.commit)

    assert '_detach_repositories' in source
    assert '_closed = True' in source
