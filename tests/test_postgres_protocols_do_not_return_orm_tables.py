from __future__ import annotations

import inspect

import src.ragforge.stores.postgres.repositories.protocols as protocols


def test_repository_protocols_do_not_expose_orm_tables() -> None:
    source = inspect.getsource(protocols)

    assert 'ProjectTable' not in source
    assert 'AssetTable' not in source
    assert 'DataChunkTable' not in source
    assert 'ProjectRecord' in source
    assert 'AssetRecord' in source
    assert 'DataChunkRecord' in source
