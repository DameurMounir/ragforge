# Branch 20 — PostgreSQL + SQLAlchemy + Alembic Production Layer

## Goal

Add a production-grade PostgreSQL persistence boundary without breaking the working RAG Core.

## What this branch adds

- PostgreSQL/PgVector-ready Docker service patch
- SQLAlchemy async session manager
- Alembic migration environment
- SQLAlchemy ORM tables for projects, assets, and chunks
- backend-neutral domain records
- repositories that do not commit
- UnitOfWork transaction ownership
- rollback-safe validation scripts
- tests for architecture rules

## Architectural flow

```text
FastAPI/service layer
  ↓
PostgresUnitOfWork
  ↓
Repositories
  ↓
Domain records + ORM mappers
  ↓
SQLAlchemy AsyncSession
  ↓
PostgreSQL
```

## Why repositories do not commit

A repository does not know the full business operation. RAGForge processing may need to delete old chunks, insert new chunks, and update the asset status as one atomic transaction.

The UnitOfWork commits only after all steps succeed.

## Asset identity rule

`asset_name` is not unique. Users may upload several files with the same original filename.

Technical uniqueness is protected by:

- `asset_uuid`
- `project_pk + stored_filename`
- `project_pk + storage_path`

## Validation

```bash
python -m compileall src/ragforge migrations scripts/validation tests
alembic -c alembic.ini upgrade head
python scripts/validation/validate_branch_20_alembic_state.py
python scripts/validation/validate_branch_20_postgres_production_layer.py
pytest
```

## Definition of Done

- PostgreSQL service starts.
- Alembic migration upgrades successfully.
- Two assets with the same original filename can exist.
- Duplicate stored filename is blocked.
- Chunk replacement works atomically.
- Repositories have no internal commit calls.
- UnitOfWork owns commit and rollback.
- Existing MongoDB/Qdrant RAG Core remains unaffected.
