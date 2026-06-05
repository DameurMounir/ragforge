from __future__ import annotations

from sqlalchemy import Index, UniqueConstraint

from src.ragforge.stores.postgres.models.asset import AssetTable
from src.ragforge.stores.postgres.models.data_chunk import DataChunkTable


def test_asset_name_is_not_unique_identifier() -> None:
    """Users may upload the same original filename multiple times."""

    constraints = [item for item in AssetTable.__table_args__ if isinstance(item, UniqueConstraint)]
    unique_column_sets = {tuple(column.name for column in constraint.columns) for constraint in constraints}

    assert ('project_pk', 'asset_name') not in unique_column_sets


def test_asset_has_partial_unique_technical_identity_indexes() -> None:
    indexes = [item for item in AssetTable.__table_args__ if isinstance(item, Index)]
    index_names = {index.name for index in indexes}

    assert 'uq_assets_project_stored_filename' in index_names
    assert 'uq_assets_project_storage_path' in index_names


def test_data_chunks_are_unique_by_asset_and_order() -> None:
    constraints = [item for item in DataChunkTable.__table_args__ if isinstance(item, UniqueConstraint)]
    unique_column_sets = {tuple(column.name for column in constraint.columns) for constraint in constraints}

    assert ('asset_pk', 'chunk_order') in unique_column_sets
