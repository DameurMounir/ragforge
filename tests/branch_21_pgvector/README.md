# Branch 21 PgVector tests

This folder isolates all tests added for Branch 21.

## Run only Branch 21 tests

```bash
pytest tests/branch_21_pgvector
```

## Run full quality gate

```bash
python -m compileall src/ragforge migrations scripts/validation tests
alembic -c alembic.ini upgrade head
alembic -c alembic.ini current
python scripts/validation/validate_branch_21_pgvector_provider.py
pytest tests/branch_21_pgvector
pytest
```

## Purpose

These tests protect the Branch 21 architecture decisions:

- Vector DB provider contract is async.
- Qdrant remains compatible.
- PgVector becomes a provider, not a service-layer special case.
- No hidden factory defaults.
- No hardcoded vector dimension.
- `EMBEDDING_VECTOR_SIZE` is the source of truth.
- `PGVECTOR_VECTOR_SIZE` is optional and must match when set.
- PgVector uses one logical `vector_records` table, not dynamic project tables.
- PgVector SQL is constrained and identifier-safe.
- PgVector index SQL is generated from config.
- Indexing reset removes stale vectors before reinserting fresh records.
- Semantic search stays provider-neutral.
