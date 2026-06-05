from __future__ import annotations

import inspect

from src.ragforge.stores.postgres.repositories import (
    PostgresAssetRepository,
    PostgresChunkRepository,
    PostgresProjectRepository,
)


def test_repositories_do_not_commit_transactions() -> None:
    """Repositories must not own commit policy."""

    for repository_cls in (
        PostgresProjectRepository,
        PostgresAssetRepository,
        PostgresChunkRepository,
    ):
        source = inspect.getsource(repository_cls)
        assert '.commit(' not in source


def test_repositories_do_flush_when_they_write() -> None:
    """Repositories may flush to expose database-generated values inside a transaction."""

    assert '.flush(' in inspect.getsource(PostgresAssetRepository)
    assert '.flush(' in inspect.getsource(PostgresChunkRepository)
