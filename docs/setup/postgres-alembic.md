# PostgreSQL and Alembic setup

Branch 20 adds a PostgreSQL persistence boundary for RAGForge.

## Start services

```bash
sudo service docker start
docker compose --env-file .env -f docker/docker-compose.yml up -d
```

## Run migrations

```bash
alembic -c alembic.ini upgrade head
alembic -c alembic.ini current
```

## Validate

```bash
python scripts/validation/validate_branch_20_alembic_state.py
python scripts/validation/validate_branch_20_postgres_production_layer.py
```

## Design rules

- The current MongoDB stores remain available.
- PostgreSQL repositories do not commit.
- UnitOfWork commits once at the end of the business operation.
- Asset display names may repeat.
- `stored_filename` and `storage_path` are the technical uniqueness keys.
