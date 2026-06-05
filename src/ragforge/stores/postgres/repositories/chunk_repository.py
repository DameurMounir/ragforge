from __future__ import annotations

import hashlib
from typing import Any

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.ragforge.stores.postgres.models.data_chunk import DataChunkTable
from src.ragforge.stores.postgres.records import DataChunkRecord
from src.ragforge.stores.postgres.repositories.mappers import chunk_to_record


class PostgresChunkRepository:
    """
    PostgreSQL repository for extracted data chunks.

    This repository does not commit. Transaction ownership belongs to
    PostgresUnitOfWork or the calling service layer.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def _text_hash(text_value: str) -> str:
        """Return a deterministic SHA-256 hash for chunk text."""

        return hashlib.sha256(text_value.encode('utf-8')).hexdigest()

    @staticmethod
    def _optional_int(value: Any) -> int | None:
        """Convert optional numeric metadata to int while preserving None.

        Extractors may return page numbers or character offsets as integers or
        numeric strings. Empty strings are treated as missing values.
        """

        if value is None or value == '':
            return None
        return int(value)

    async def insert_many(
        self,
        project_pk: int,
        asset_pk: int,
        chunks: list[dict[str, Any]],
    ) -> int:
        """
        Insert many chunks in one SQL statement.

        Empty chunks are skipped. Chunk order defaults to the source list index
        if the input does not provide `chunk_order`.
        """

        rows: list[dict[str, Any]] = []

        for index, chunk in enumerate(chunks, start=1):
            text_value = str(chunk.get('chunk_text') or chunk.get('text') or '').strip()
            if not text_value:
                continue

            # Preserve zero-valued metadata. PDF loaders often use page 0 for the
            # first page, so `or` fallback would incorrectly convert 0 to None.
            page_number = chunk.get('page_number')
            if page_number is None:
                page_number = chunk.get('page')

            chunk_order_value = chunk.get('chunk_order')
            if chunk_order_value is None:
                chunk_order_value = index

            rows.append(
                {
                    'project_pk': project_pk,
                    'asset_pk': asset_pk,
                    'chunk_text': text_value,
                    'chunk_order': int(chunk_order_value),
                    'text_hash': str(chunk.get('text_hash') or self._text_hash(text_value)),
                    'page_number': self._optional_int(page_number),
                    'char_start': self._optional_int(chunk.get('char_start')),
                    'char_end': self._optional_int(chunk.get('char_end')),
                    'chunk_metadata': chunk.get('metadata') or chunk.get('chunk_metadata') or {},
                    'embedded': bool(chunk.get('embedded', False)),
                    'embedding_model': chunk.get('embedding_model'),
                    'indexed_in_vector_store': bool(chunk.get('indexed_in_vector_store', False)),
                    'vector_record_id': chunk.get('vector_record_id'),
                }
            )

        if not rows:
            return 0

        await self.session.execute(insert(DataChunkTable), rows)
        await self.session.flush()
        return len(rows)

    async def replace_asset_chunks(
        self,
        project_pk: int,
        asset_pk: int,
        chunks: list[dict[str, Any]],
    ) -> int:
        """
        Delete old chunks for an asset and insert the new chunk set.

        The caller's Unit of Work commits or rolls back the whole operation.
        This makes reprocessing atomic: old chunks are not lost if insertion
        fails halfway.
        """

        await self.delete_by_asset(asset_pk=asset_pk)
        return await self.insert_many(
            project_pk=project_pk,
            asset_pk=asset_pk,
            chunks=chunks,
        )

    async def list_project_chunks(
        self,
        project_pk: int,
        limit: int | None = None,
    ) -> list[DataChunkRecord]:
        query = (
            select(DataChunkTable)
            .where(DataChunkTable.project_pk == project_pk)
            .order_by(DataChunkTable.asset_pk.asc(), DataChunkTable.chunk_order.asc())
        )

        if limit is not None:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return [chunk_to_record(row) for row in result.scalars().all()]

    async def delete_by_asset(self, asset_pk: int) -> int:
        result = await self.session.execute(
            delete(DataChunkTable).where(DataChunkTable.asset_pk == asset_pk)
        )
        await self.session.flush()
        return int(result.rowcount or 0)

    async def delete_by_project(self, project_pk: int) -> int:
        result = await self.session.execute(
            delete(DataChunkTable).where(DataChunkTable.project_pk == project_pk)
        )
        await self.session.flush()
        return int(result.rowcount or 0)

    async def mark_embedded(
        self,
        chunk_ids: list[int],
        embedding_model: str,
    ) -> int:
        if not chunk_ids:
            return 0

        result = await self.session.execute(
            update(DataChunkTable)
            .where(DataChunkTable.id.in_(chunk_ids))
            .values(embedded=True, embedding_model=embedding_model)
        )
        await self.session.flush()
        return int(result.rowcount or 0)

    async def mark_indexed_in_vector_store(
        self,
        chunk_vector_record_ids: dict[int, str],
    ) -> int:
        """Mark chunks as indexed and persist their vector-store record IDs.

        `vector_record_id` is part of the relational audit trail. A chunk should
        not be marked as indexed without knowing the ID of the corresponding
        point/record in the vector store.
        """

        if not chunk_vector_record_ids:
            return 0

        updated = 0
        for chunk_id, vector_record_id in chunk_vector_record_ids.items():
            result = await self.session.execute(
                update(DataChunkTable)
                .where(DataChunkTable.id == int(chunk_id))
                .values(
                    indexed_in_vector_store=True,
                    vector_record_id=str(vector_record_id),
                )
            )
            updated += int(result.rowcount or 0)

        await self.session.flush()
        return updated
