from __future__ import annotations

import json
import re
from typing import Any

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.ragforge.providers.vector_db.base import BaseVectorDBProvider
from src.ragforge.providers.vector_db.enums import (
    DistanceMethod,
    PgVectorIndexType,
    PgVectorIndexVectorType,
)
from src.ragforge.providers.vector_db.exceptions import (
    VectorDBConfigurationError,
    VectorDBProviderError,
)
from src.ragforge.providers.vector_db.schemas import (
    VectorRecord,
    VectorSearchResult,
)
from src.ragforge.stores.postgres.session import PostgresSessionManager

_IDENTIFIER_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
_METADATA_KEY_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


class PgVectorProvider(BaseVectorDBProvider):
    """
    PgVector implementation of the RAGForge vector DB provider.

    Branch 21 v4 rules:
    - no provider defaults are hidden inside this class
    - all operational values come from core/config.py through the factory
    - collection_name is a logical namespace, not a dynamic table name
    - the table is Alembic-managed and stores variable-dimension vectors
    - vector_size is validated at runtime and in PostgreSQL
    - index expression type is configurable: vector or halfvec
    """

    SUPPORTED_INDEX_TYPES = {
        PgVectorIndexType.HNSW.value,
        PgVectorIndexType.IVFFLAT.value,
    }

    SUPPORTED_INDEX_VECTOR_TYPES = {
        PgVectorIndexVectorType.VECTOR.value,
        PgVectorIndexVectorType.HALFVEC.value,
    }

    DISTANCE_OPERATORS = {
        DistanceMethod.COSINE.value: '<=>',
        DistanceMethod.EUCLID.value: '<->',
        DistanceMethod.DOT.value: '<#>',
    }

    VECTOR_OPERATOR_CLASSES = {
        DistanceMethod.COSINE.value: 'vector_cosine_ops',
        DistanceMethod.EUCLID.value: 'vector_l2_ops',
        DistanceMethod.DOT.value: 'vector_ip_ops',
    }

    HALFVEC_OPERATOR_CLASSES = {
        DistanceMethod.COSINE.value: 'halfvec_cosine_ops',
        DistanceMethod.EUCLID.value: 'halfvec_l2_ops',
        DistanceMethod.DOT.value: 'halfvec_ip_ops',
    }

    # PgVector approximate indexes have documented dimension limits by indexed type.
    # These are provider capability limits, not application defaults.
    INDEX_VECTOR_MAX_DIMS = {
        PgVectorIndexVectorType.VECTOR.value: 2000,
        PgVectorIndexVectorType.HALFVEC.value: 4000,
    }

    def __init__(
        self,
        session_manager: PostgresSessionManager,
        table_name: str,
        vector_size: int,
        distance: str,
        index_type: str,
        index_vector_type: str,
        hnsw_m: int,
        hnsw_ef_construction: int,
        hnsw_ef_search: int,
        ivfflat_lists: int,
        ivfflat_probes: int,
        index_min_records: int,
        auto_create_index: bool,
        create_extension_on_startup: bool,
        embedding_model: str,
        embedding_provider: str,
    ) -> None:
        self.session_manager = session_manager
        self.table_name = self._validate_identifier(table_name, 'table_name')
        self.vector_size = self._validate_positive_int(vector_size, 'vector_size')
        self.distance = str(distance)
        self.index_type = str(index_type)
        self.index_vector_type = str(index_vector_type)
        self.hnsw_m = self._validate_positive_int(hnsw_m, 'hnsw_m')
        self.hnsw_ef_construction = self._validate_positive_int(
            hnsw_ef_construction,
            'hnsw_ef_construction',
        )
        self.hnsw_ef_search = self._validate_positive_int(
            hnsw_ef_search,
            'hnsw_ef_search',
        )
        self.ivfflat_lists = self._validate_positive_int(
            ivfflat_lists,
            'ivfflat_lists',
        )
        self.ivfflat_probes = self._validate_positive_int(
            ivfflat_probes,
            'ivfflat_probes',
        )
        self.index_min_records = int(index_min_records)
        if self.index_min_records < 0:
            raise VectorDBConfigurationError(
                f'index_min_records must be >= 0. Received: {index_min_records}'
            )
        self.auto_create_index = bool(auto_create_index)
        self.create_extension_on_startup = bool(create_extension_on_startup)
        self.embedding_model = str(embedding_model)
        self.embedding_provider = str(embedding_provider)
        if not self.embedding_model.strip():
            raise VectorDBConfigurationError('embedding_model must be configured.')
        if not self.embedding_provider.strip():
            raise VectorDBConfigurationError('embedding_provider must be configured.')
        self._connected = False

        self._validate_supported_mode()

    def _validate_supported_mode(self) -> None:
        if self.distance not in self.DISTANCE_OPERATORS:
            raise VectorDBConfigurationError(
                f'Unsupported PgVector distance method: {self.distance}'
            )

        if self.index_type not in self.SUPPORTED_INDEX_TYPES:
            raise VectorDBConfigurationError(
                f'Unsupported PgVector index type: {self.index_type}'
            )

        if self.index_vector_type not in self.SUPPORTED_INDEX_VECTOR_TYPES:
            raise VectorDBConfigurationError(
                f'Unsupported PgVector index vector type: {self.index_vector_type}'
            )

        max_dims = self.INDEX_VECTOR_MAX_DIMS[self.index_vector_type]
        if self.vector_size > max_dims:
            raise VectorDBConfigurationError(
                f'PgVector {self.index_vector_type} index supports up to '
                f'{max_dims} dimensions; configured vector_size={self.vector_size}.'
            )

    @staticmethod
    def _validate_identifier(value: str, label: str) -> str:
        if not _IDENTIFIER_RE.fullmatch(str(value)):
            raise VectorDBConfigurationError(
                f'Invalid PostgreSQL identifier for {label}: {value}'
            )
        return str(value)

    @staticmethod
    def _validate_metadata_key(value: str) -> str:
        if not _METADATA_KEY_RE.fullmatch(str(value)):
            raise VectorDBProviderError(f'Invalid metadata filter key: {value}')
        return str(value)

    @staticmethod
    def _validate_positive_int(value: int | None, label: str) -> int:
        if value is None:
            raise VectorDBConfigurationError(f'{label} must be configured.')
        try:
            int_value = int(value)
        except (TypeError, ValueError) as error:
            raise VectorDBConfigurationError(
                f'{label} must be a positive integer. Received: {value}'
            ) from error
        if int_value <= 0:
            raise VectorDBConfigurationError(
                f'{label} must be a positive integer. Received: {value}'
            )
        return int_value

    def _validate_vector_size(self, vector: list[float]) -> None:
        if len(vector) != self.vector_size:
            raise VectorDBProviderError(
                f'PgVector provider is configured for vectors of size '
                f'{self.vector_size}; received {len(vector)}.'
            )

    def _vector_to_pg_literal(self, vector: list[float]) -> str:
        if not vector:
            raise VectorDBProviderError('Vector must not be empty.')
        self._validate_vector_size(vector)
        return '[' + ','.join(format(float(item), '.12g') for item in vector) + ']'

    @staticmethod
    def _record_id(record: VectorRecord) -> str:
        if record.record_id is None:
            raise VectorDBProviderError('VectorRecord.record_id is required for PgVector.')
        return str(record.record_id)

    @staticmethod
    def _metadata_to_json(metadata: dict[str, Any]) -> str:
        if not isinstance(metadata, dict):
            raise VectorDBProviderError('VectorRecord.metadata must be a dictionary.')
        return json.dumps(metadata, ensure_ascii=False, default=str)

    def _distance_operator(self) -> str:
        return self.DISTANCE_OPERATORS[self.distance]

    def _operator_class(self) -> str:
        if self.index_vector_type == PgVectorIndexVectorType.VECTOR.value:
            return self.VECTOR_OPERATOR_CLASSES[self.distance]
        if self.index_vector_type == PgVectorIndexVectorType.HALFVEC.value:
            return self.HALFVEC_OPERATOR_CLASSES[self.distance]
        raise VectorDBConfigurationError(
            f'Unsupported PgVector index vector type: {self.index_vector_type}'
        )

    def _index_name(self) -> str:
        return self._validate_identifier(
            (
                f'ix_{self.table_name}_embedding_'
                f'{self.index_type}_{self.distance}_'
                f'{self.index_vector_type}_{self.vector_size}'
            ),
            'index_name',
        )

    def _typed_embedding_expression(self) -> str:
        return f'(embedding::{self.index_vector_type}({self.vector_size}))'

    def _typed_query_expression(self) -> str:
        return f'CAST(:query_vector AS {self.index_vector_type}({self.vector_size}))'

    def _score_from_distance(self, distance: float) -> float:
        distance_value = float(distance)
        if self.distance == DistanceMethod.COSINE.value:
            return 1.0 - distance_value
        if self.distance == DistanceMethod.DOT.value:
            # PgVector inner-product operator returns the negative inner product
            # so ASC ordering works with indexes. Convert back to higher-is-better.
            return -distance_value
        if self.distance == DistanceMethod.EUCLID.value:
            return 1.0 / (1.0 + distance_value)
        raise VectorDBConfigurationError(
            f'Unsupported PgVector distance method: {self.distance}'
        )

    async def connect(self) -> None:
        if self.create_extension_on_startup:
            async with self.session_manager.session() as session:
                await session.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))
                await session.commit()
        self._connected = True

    async def disconnect(self) -> None:
        await self.session_manager.dispose()
        self._connected = False

    def _require_connected(self) -> None:
        if not self._connected:
            raise VectorDBProviderError(
                'PgVector provider is not connected. Call connect() first.'
            )

    async def _configured_dimension_record_count(self) -> int:
        async with self.session_manager.session() as session:
            result = await session.execute(
                text(
                    f'SELECT COUNT(*) FROM {self.table_name} '
                    'WHERE vector_size = :vector_size'
                ),
                {'vector_size': self.vector_size},
            )
            return int(result.scalar_one() or 0)

    async def _ensure_vector_index(self) -> bool:
        """
        Create a provider-managed approximate index for the configured dimension.

        The table is Alembic-managed. The vector index is runtime/config-managed
        because PgVector requires expression/partial indexes when one column can
        store multiple vector dimensions.
        """
        if not self.auto_create_index:
            return False

        if (
            self.index_type == PgVectorIndexType.IVFFLAT.value
            and self.index_min_records > 0
        ):
            record_count = await self._configured_dimension_record_count()
            if record_count < self.index_min_records:
                return False

        index_name = self._index_name()
        operator_class = self._operator_class()
        embedding_expression = self._typed_embedding_expression()

        if self.index_type == PgVectorIndexType.HNSW.value:
            ddl = (
                f'CREATE INDEX IF NOT EXISTS {index_name} '
                f'ON {self.table_name} USING hnsw '
                f'({embedding_expression} {operator_class}) '
                f'WITH (m = {self.hnsw_m}, '
                f'ef_construction = {self.hnsw_ef_construction}) '
                f'WHERE vector_size = {self.vector_size}'
            )
        elif self.index_type == PgVectorIndexType.IVFFLAT.value:
            ddl = (
                f'CREATE INDEX IF NOT EXISTS {index_name} '
                f'ON {self.table_name} USING ivfflat '
                f'({embedding_expression} {operator_class}) '
                f'WITH (lists = {self.ivfflat_lists}) '
                f'WHERE vector_size = {self.vector_size}'
            )
        else:
            raise VectorDBConfigurationError(
                f'Unsupported PgVector index type: {self.index_type}'
            )

        async with self.session_manager.session() as session:
            await session.execute(text(ddl))
            await session.commit()
        return True

    async def collection_exists(self, collection_name: str) -> bool:
        self._require_connected()
        async with self.session_manager.session() as session:
            result = await session.execute(
                text(
                    f'SELECT 1 FROM {self.table_name} '
                    'WHERE collection_name = :collection_name LIMIT 1'
                ),
                {'collection_name': collection_name},
            )
            return result.scalar_one_or_none() is not None

    async def list_collections(self) -> list[str]:
        self._require_connected()
        async with self.session_manager.session() as session:
            result = await session.execute(
                text(
                    f'SELECT DISTINCT collection_name FROM {self.table_name} '
                    'ORDER BY collection_name'
                )
            )
            return [str(row[0]) for row in result.fetchall()]

    async def get_collection_info(self, collection_name: str) -> dict[str, Any]:
        self._require_connected()
        async with self.session_manager.session() as session:
            result = await session.execute(
                text(
                    f'SELECT COUNT(*) AS total_records, '
                    'COUNT(DISTINCT project_id) AS total_projects, '
                    'COUNT(DISTINCT asset_id) AS total_assets, '
                    'COUNT(DISTINCT vector_size) AS total_vector_sizes '
                    f'FROM {self.table_name} '
                    'WHERE collection_name = :collection_name'
                ),
                {'collection_name': collection_name},
            )
            row = result.mappings().one()
            return {
                'collection_name': collection_name,
                'table_name': self.table_name,
                'total_records': int(row['total_records'] or 0),
                'total_projects': int(row['total_projects'] or 0),
                'total_assets': int(row['total_assets'] or 0),
                'total_vector_sizes': int(row['total_vector_sizes'] or 0),
                'distance': self.distance,
                'index_type': self.index_type,
                'index_vector_type': self.index_vector_type,
                'vector_size': self.vector_size,
                'index_name': self._index_name(),
            }

    async def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: str,
        do_reset: bool = False,
    ) -> bool:
        self._require_connected()

        if int(vector_size) != self.vector_size:
            raise VectorDBConfigurationError(
                f'PgVector provider expects vector_size={self.vector_size}; '
                f'received {vector_size}.'
            )

        if distance != self.distance:
            raise VectorDBConfigurationError(
                f'PgVector provider configured for {self.distance}; received {distance}.'
            )

        if do_reset:
            await self.delete_collection(collection_name=collection_name)

        await self._ensure_vector_index()
        return True

    async def delete_collection(self, collection_name: str) -> bool:
        deleted = await self.delete_records(
            collection_name=collection_name,
            filters=None,
        )
        return deleted > 0

    async def delete_records(
        self,
        collection_name: str,
        filters: dict | None = None,
    ) -> int:
        self._require_connected()
        filter_clause, filter_params = self._build_filter_clause(filters)
        async with self.session_manager.session() as session:
            result = await session.execute(
                text(
                    f'DELETE FROM {self.table_name} '
                    'WHERE collection_name = :collection_name '
                    f'{filter_clause}'
                ),
                {'collection_name': collection_name, **filter_params},
            )
            await session.commit()
            return int(result.rowcount or 0)

    def _row_from_record(self, collection_name: str, record: VectorRecord) -> dict[str, Any]:
        metadata = dict(record.metadata or {})
        embedding_model = metadata.get('embedding_model') or self.embedding_model
        embedding_provider = metadata.get('embedding_provider') or self.embedding_provider

        metadata['embedding_model'] = str(embedding_model)
        metadata['embedding_provider'] = str(embedding_provider)

        return {
            'collection_name': collection_name,
            'record_id': self._record_id(record),
            'text': record.text,
            'embedding': self._vector_to_pg_literal(record.vector),
            'vector_size': self.vector_size,
            'embedding_model': str(embedding_model),
            'embedding_provider': str(embedding_provider),
            'project_id': metadata.get('project_id'),
            'asset_id': metadata.get('asset_id'),
            'chunk_id': metadata.get('chunk_id'),
            'chunk_order': metadata.get('chunk_order'),
            'metadata': self._metadata_to_json(metadata),
        }

    async def insert_one(
        self,
        collection_name: str,
        record: VectorRecord,
    ) -> bool:
        inserted = await self.insert_many(
            collection_name=collection_name,
            records=[record],
            batch_size=1,
        )
        return inserted == 1

    async def insert_many(
        self,
        collection_name: str,
        records: list[VectorRecord],
        batch_size: int = 64,
    ) -> int:
        self._require_connected()
        if not records:
            return 0

        insert_sql = text(
            f'INSERT INTO {self.table_name} ('
            'collection_name, record_id, text, embedding, vector_size, '
            'embedding_model, embedding_provider, project_id, asset_id, '
            'chunk_id, chunk_order, metadata'
            ') VALUES ('
            ':collection_name, :record_id, :text, CAST(:embedding AS vector), '
            ':vector_size, :embedding_model, :embedding_provider, :project_id, '
            ':asset_id, :chunk_id, :chunk_order, CAST(:metadata AS jsonb)'
            ') '
            'ON CONFLICT ('
            'collection_name, record_id, embedding_provider, embedding_model, vector_size'
            ') DO UPDATE SET '
            'text = EXCLUDED.text, '
            'embedding = EXCLUDED.embedding, '
            'project_id = EXCLUDED.project_id, '
            'asset_id = EXCLUDED.asset_id, '
            'chunk_id = EXCLUDED.chunk_id, '
            'chunk_order = EXCLUDED.chunk_order, '
            'metadata = EXCLUDED.metadata, '
            'updated_at = now()'
        )

        inserted_count = 0
        try:
            async with self.session_manager.session() as session:
                for start in range(0, len(records), batch_size):
                    batch = records[start : start + batch_size]
                    rows = [self._row_from_record(collection_name, record) for record in batch]
                    await session.execute(insert_sql, rows)
                    inserted_count += len(rows)
                await session.commit()

            await self._ensure_vector_index()
        except SQLAlchemyError as error:
            raise VectorDBProviderError(f'PgVector insert_many failed: {error}') from error

        return inserted_count

    def _build_filter_clause(self, filters: dict | None) -> tuple[str, dict[str, Any]]:
        clauses = ['vector_size = :configured_vector_size']
        params: dict[str, Any] = {'configured_vector_size': self.vector_size}

        if not filters:
            return ' AND ' + ' AND '.join(clauses), params

        column_filters = {
            'project_id',
            'asset_id',
            'chunk_id',
            'embedding_model',
            'embedding_provider',
            'vector_size',
        }

        for index, (key, value) in enumerate(filters.items()):
            safe_key = self._validate_metadata_key(str(key))
            if safe_key == 'vector_size':
                param_name = f'filter_value_{index}'
                clauses.append(f'vector_size = :{param_name}')
                params[param_name] = self._validate_positive_int(value, 'vector_size')
            elif safe_key in column_filters:
                param_name = f'filter_value_{index}'
                clauses.append(f'{safe_key} = :{param_name}')
                params[param_name] = str(value)
            else:
                key_param = f'filter_key_{index}'
                value_param = f'filter_value_{index}'
                clauses.append(f'metadata ->> :{key_param} = :{value_param}')
                params[key_param] = safe_key
                params[value_param] = str(value)

        return ' AND ' + ' AND '.join(clauses), params

    async def search_by_vector(
        self,
        collection_name: str,
        vector: list[float],
        limit: int = 10,
        filters: dict | None = None,
    ) -> list[VectorSearchResult]:
        self._require_connected()
        operator = self._distance_operator()
        embedding_expression = self._typed_embedding_expression()
        query_expression = self._typed_query_expression()
        query_vector = self._vector_to_pg_literal(vector)
        filter_clause, filter_params = self._build_filter_clause(filters)

        search_sql = text(
            'SELECT record_id, text, metadata, '
            f'({embedding_expression} {operator} {query_expression}) AS distance '
            f'FROM {self.table_name} '
            'WHERE collection_name = :collection_name '
            f'{filter_clause} '
            f'ORDER BY {embedding_expression} {operator} {query_expression} ASC '
            'LIMIT :limit'
        )

        params: dict[str, Any] = {
            'collection_name': collection_name,
            'query_vector': query_vector,
            'limit': int(limit),
        }
        params.update(filter_params)

        async with self.session_manager.session() as session:
            if self.index_type == PgVectorIndexType.HNSW.value:
                await session.execute(
                    text(f'SET LOCAL hnsw.ef_search = {self.hnsw_ef_search}')
                )
            elif self.index_type == PgVectorIndexType.IVFFLAT.value:
                await session.execute(
                    text(f'SET LOCAL ivfflat.probes = {self.ivfflat_probes}')
                )
            result = await session.execute(search_sql, params)
            rows = result.mappings().all()

        results: list[VectorSearchResult] = []
        for row in rows:
            metadata = dict(row['metadata'] or {})
            distance = float(row['distance'])
            results.append(
                VectorSearchResult(
                    record_id=row['record_id'],
                    score=self._score_from_distance(distance),
                    text=row['text'],
                    metadata=metadata,
                )
            )
        return results
