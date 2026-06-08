# Production Docker Runtime Setup

Branch 22 adds a production-like Docker runtime and observability foundation for RAGForge.

This branch does **not** add GitHub Actions or VPS automation. That belongs to the next deployment branch.

## Runtime stack

```text
Nginx
  ↓
RAGForge FastAPI container
  ↓
MongoDB metadata and chunks
  ↓
PostgreSQL / PgVector
  ↓
Qdrant optional vector backend
  ↓
Prometheus metrics collection
  ↓
Grafana dashboards and provisioned Prometheus data source
```

## Services

| Service | Purpose |
|---|---|
| `ragforge-api` | FastAPI application container |
| `nginx` | Reverse proxy in front of the API |
| `mongodb` | Current project, asset, and chunk metadata store |
| `postgres` | PostgreSQL database with PgVector extension |
| `qdrant` | Optional vector backend preserved for provider switching |
| `prometheus` | Metrics collection |
| `grafana` | Metrics dashboards |
| `postgres-exporter` | PostgreSQL metrics exporter |
| `node-exporter` | Host/system metrics exporter |

## Create runtime env files

From the repository root:

```bash
cp docker/env/.env.app.example docker/env/.env.app
cp docker/env/.env.mongodb.example docker/env/.env.mongodb
cp docker/env/.env.postgres.example docker/env/.env.postgres
cp docker/env/.env.grafana.example docker/env/.env.grafana
cp docker/env/.env.postgres-exporter.example docker/env/.env.postgres-exporter
```

Then edit secrets and provider values:

```bash
nano docker/env/.env.app
nano docker/env/.env.mongodb
nano docker/env/.env.postgres
nano docker/env/.env.grafana
nano docker/env/.env.postgres-exporter
```

For real OpenAI testing, set:

```env
LLM_PROVIDER="openai_compatible"
LLM_DEFAULT_MODEL="gpt-4o-mini"
OPENAI_API_KEY="your_key_here"
OPENAI_BASE_URL="https://api.openai.com/v1"

EMBEDDING_PROVIDER="openai_compatible"
EMBEDDING_MODEL="text-embedding-3-small"
EMBEDDING_OPENAI_API_KEY="your_key_here"
EMBEDDING_OPENAI_BASE_URL="https://api.openai.com/v1"
EMBEDDING_VECTOR_SIZE=1536

VECTOR_DB_PROVIDER="pgvector"
```

## Build and start

```bash
docker compose -f docker/docker-compose.production.yml up -d --build
```

Check containers:

```bash
docker compose -f docker/docker-compose.production.yml ps
```

Follow logs:

```bash
docker compose -f docker/docker-compose.production.yml logs -f ragforge-api
```

## Endpoints

The production compose binds services to localhost by default:

| Endpoint | URL |
|---|---|
| API through Nginx | `http://127.0.0.1:8088/api/v1/health/` |
| API direct debug port | `http://127.0.0.1:8000/api/v1/health/` |
| API metrics direct port | `http://127.0.0.1:8000/metrics` |
| Prometheus | `http://127.0.0.1:9090` |
| Grafana | `http://127.0.0.1:3000` |
| Qdrant | `http://127.0.0.1:6335/dashboard` |

The metrics endpoint is intentionally **not exposed through Nginx**. Prometheus scrapes the API through the internal Docker network.

## Validate

Static validation:

```bash
python scripts/validation/validate_branch_22_production_runtime.py
```

Runtime validation against the direct API port:

```bash
python scripts/validation/validate_branch_22_production_runtime.py --runtime --base-url http://127.0.0.1:8000
```

Runtime validation through Nginx health only:

```bash
curl -s http://127.0.0.1:8088/api/v1/health/ | python -m json.tool
```

Direct metrics validation:

```bash
curl -s http://127.0.0.1:8000/metrics | head
# Nginx intentionally does not expose metrics:
curl -i http://127.0.0.1:8088/metrics
```

## Tests

```bash
python -m compileall src/ragforge scripts/validation tests
pytest tests/branch_22_observability -q
pytest -q
```

## Docker management

Stop the stack without deleting volumes:

```bash
docker compose -f docker/docker-compose.production.yml down
```

Stop and delete volumes only when you intentionally want a clean database reset:

```bash
docker compose -f docker/docker-compose.production.yml down -v
```

List volumes:

```bash
docker volume ls | grep ragforge
```

Inspect logs:

```bash
docker compose -f docker/docker-compose.production.yml logs -f nginx
docker compose -f docker/docker-compose.production.yml logs -f prometheus
docker compose -f docker/docker-compose.production.yml logs -f grafana
```

## Design rules

- Do not commit real env files.
- Do not expose Grafana publicly by default.
- Do not expose `/metrics` through Nginx by default.
- Keep MongoDB as the current metadata/chunk store.
- Keep PgVector and Qdrant switchable through `VECTOR_DB_PROVIDER`.
- Keep Alembic migrations as the PostgreSQL schema authority.
- Keep Branch 22 focused on local/server-ready runtime. GitHub Actions deployment comes later.
