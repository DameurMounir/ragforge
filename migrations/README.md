# RAGForge database migrations

This directory contains Alembic migrations for the PostgreSQL persistence layer.

Common commands:

```bash
alembic -c alembic.ini upgrade head
alembic -c alembic.ini current
alembic -c alembic.ini history
alembic -c alembic.ini revision --autogenerate -m "describe change"
```

Branch 20 creates the relational metadata schema. It does not remove MongoDB.
