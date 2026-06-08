# Branch 22 — Production Docker Runtime & Observability Foundation

Git branch:

```text
feature/22-production-docker-observability
```

Milestone:

```text
Milestone 6 — Production Deployment & Workers
```

## Goal

Turn the Branch 21 real RAG runtime into a production-like Docker Compose stack with Nginx, Prometheus, Grafana, PostgreSQL/PgVector, MongoDB, Qdrant, and exporter-based monitoring.

Branch 22 does not introduce GitHub Actions, VPS automation, or systemd deployment. Those belong to the next branch.

## Why this branch exists

Branch 21 proved that RAGForge can run real end-to-end RAG with:

```text
FastAPI
→ MongoDB metadata/chunks
→ OpenAI text-embedding-3-small
→ PostgreSQL + PgVector vector storage
→ semantic retrieval
→ retrieval post-processing
→ GPT-4o-mini grounded answer generation
→ citation validation
```

Branch 22 wraps that working system in a production runtime shell.

## Architecture

```text
Nginx reverse proxy
  ↓
RAGForge FastAPI container
  ├── /api/v1/health/
  ├── /api/v1/documents/upload/{project_id}
  ├── /api/v1/documents/process/{project_id}
  ├── /api/v1/indexing/{project_id}
  ├── /api/v1/search/{project_id}
  ├── /api/v1/answers/{project_id}
  └── /metrics
       ↓
MongoDB metadata and chunks
       ↓
PostgreSQL / PgVector vector_records
       ↓
Qdrant optional vector backend
       ↓
Prometheus scraping
       ↓
Grafana dashboards and provisioned Prometheus data source
```

## Main changes

- Add production Docker Compose stack.
- Use an isolated Compose project name without fixed container names to avoid conflicts with the Branch 21 development stack.
- Add RAGForge API Dockerfile.
- Add RAGForge container entrypoint that prepares Prometheus multiprocess state and then execs the requested command.
- Run Alembic migrations through a one-shot `ragforge-migrations` service before the API starts.
- Add Nginx reverse proxy configuration.
- Add Prometheus configuration.
- Add Grafana service.
- Add Postgres exporter.
- Add Node exporter.
- Add configurable FastAPI Prometheus metrics middleware.
- Add `/metrics` endpoint behind `METRICS_ENABLED` and `METRICS_PATH` settings.
- Avoid high-cardinality metrics labels by using FastAPI route templates.
- Keep metrics hidden from the public Nginx route by default.
- Add Docker env example files without committing secrets.
- Add Branch 22 validation script and tests.

## Design decisions

### Metrics route is configurable

The metrics route is controlled by:

```env
METRICS_ENABLED=true
METRICS_PATH="/metrics"
METRICS_INCLUDE_IN_SCHEMA=false
```

The endpoint is excluded from OpenAPI docs by default.

### Prometheus uses low-cardinality labels

The middleware records route templates such as:

```text
/api/v1/documents/upload/{project_id}
```

instead of raw paths such as:

```text
/api/v1/documents/upload/fastapi
/api/v1/documents/upload/project42
```

This avoids exploding the Prometheus time-series count.

### Nginx does not expose metrics publicly

Prometheus scrapes `ragforge-api:8000/metrics` from the internal Docker network.

Nginx returns `404` for `/metrics` by default.

### Branch 22 does not remove MongoDB

MongoDB remains the current RAGForge ingestion metadata store.

PostgreSQL/PgVector remains the active vector backend when:

```env
VECTOR_DB_PROVIDER="pgvector"
```

Qdrant remains available when:

```env
VECTOR_DB_PROVIDER="qdrant"
```

## Files added

```text
docker/docker-compose.production.yml
docker/ragforge/Dockerfile
docker/ragforge/entrypoint.sh
docker/nginx/default.conf
docker/prometheus/prometheus.yml
docker/env/.env.app.example
docker/env/.env.mongodb.example
docker/env/.env.postgres.example
docker/env/.env.grafana.example
docker/env/.env.postgres-exporter.example
docker/.gitignore
.dockerignore
requirements_branch22_additions.txt
src/ragforge/observability/__init__.py
src/ragforge/observability/metrics.py
scripts/validation/validate_branch_22_production_runtime.py
tests/branch_22_observability/test_metrics_middleware.py
docs/setup/production-docker-runtime.md
docs/milestones/milestone-06-production-deployment-workers/branches/branch-22-production-docker-observability.md
```

## Files updated

```text
requirements.txt
src/ragforge/core/config.py
src/ragforge/main.py
.env.example
.gitignore
README.md
```

## Definition of done

- RAGForge API image builds successfully.
- Docker Compose starts all runtime services.
- MongoDB is healthy.
- PostgreSQL/PgVector is healthy.
- Qdrant starts successfully.
- Alembic migrations run once through the `ragforge-migrations` service before the API container starts.
- API health works through direct port and Nginx.
- `/metrics` works through the internal API port.
- `/metrics` is not exposed through Nginx by default.
- Prometheus can scrape RAGForge API metrics.
- Prometheus can scrape Postgres exporter.
- Prometheus can scrape Qdrant metrics.
- Prometheus can scrape Node exporter metrics.
- Grafana starts with persistent storage.
- Metrics tests pass.
- Full test suite passes.

## Validation

```bash
python -m compileall src/ragforge scripts/validation tests
python scripts/validation/validate_branch_22_production_runtime.py
pytest tests/branch_22_observability -q
pytest -q
```

Production runtime validation:

```bash
cp docker/env/.env.app.example docker/env/.env.app
cp docker/env/.env.mongodb.example docker/env/.env.mongodb
cp docker/env/.env.postgres.example docker/env/.env.postgres
cp docker/env/.env.grafana.example docker/env/.env.grafana
cp docker/env/.env.postgres-exporter.example docker/env/.env.postgres-exporter

docker compose -f docker/docker-compose.production.yml up -d --build
docker compose -f docker/docker-compose.production.yml ps

curl -s http://127.0.0.1:8088/api/v1/health/ | python -m json.tool
curl -s http://127.0.0.1:8000/metrics | head
# Nginx intentionally does not expose metrics:
curl -i http://127.0.0.1:8088/metrics

python scripts/validation/validate_branch_22_production_runtime.py --runtime --base-url http://127.0.0.1:8000
```

## Next branch

Branch 23 should add server deployment automation:

```text
Ubuntu VPS
SSH deployment user
Deploy keys
Docker installation on server
systemd service
firewall rules
SSH port forwarding for Grafana
GitHub Actions secrets
GitHub Actions deployment workflow
```
