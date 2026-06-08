# 🛠️ RAGForge

**RAGForge** is a production-oriented **Retrieval-Augmented Generation (RAG)** backend platform built step by step with real software engineering practices.

The project starts from a clean FastAPI backend and progressively evolves toward document ingestion, project-based storage, metadata management, text extraction, chunking, LLM integration, vector databases, embeddings, indexing, semantic search, grounded answer generation, production persistence, background workers, observability, security, and production deployment.

RAGForge is not a notebook demo. It is designed as a long-term AI engineering project focused on building a clean, scalable, and professional backend architecture.

---

## 🎯 Project Vision

RAGForge aims to become a modular foundation for building production-ready RAG systems.

The objective is to master the full engineering path from a basic backend service to a production-ready AI platform that can later be reused by applications, websites, internal tools, or agent systems as a reliable knowledge backend.

RAGForge is also designed as one infrastructure brick inside a broader agentic systems architecture. It is not limited to naive RAG. It prepares the foundation for retrieval tools, answer-generation tools, source-grounded knowledge access, orchestration layers, observability, and future AI system components.

---

## 🧠 Knowledge-Oriented RAG Direction

RAGForge is built with the understanding that **RAG is not dead**.

What is becoming obsolete is **naive RAG**: systems that only split documents into chunks, retrieve a few similar passages, and pass them directly to an LLM without strong metadata, structure, provenance, indexing, source control, retrieval strategy, citation validation, or workflow discipline.

RAGForge follows a more modern **knowledge-oriented RAG direction**.

The goal is to evolve from simple document retrieval toward a production-grade knowledge backend where every source is tracked as an asset, every extracted chunk is linked to its origin, metadata is persisted, vectors are indexed, semantic search returns source-ready evidence, grounded answers can be generated with structured sources, and production persistence can evolve safely through migrations.

The current architectural direction is:

```text
Project
  ↓
Asset
  ↓
DataChunk
  ↓
Embedding
  ↓
Vector Indexing
  ↓
Semantic Search
  ↓
Retrieval Post-processing
  ↓
Grounded / Augmented Answer with Sources
  ↓
Citation Validation
  ↓
Production Persistence / Workers / Observability
```

This makes RAGForge more than a basic RAG demo. It is designed as a foundation for structured knowledge systems that can later support applications, websites, internal tools, and agentic AI workflows.

---

## 🧭 7-Milestone Roadmap

| Milestone | Focus | Expected Result |
|---|---|---|
| M1 | 🧱 Project Bootstrap & Environment | Repository, environment, Git workflow, README, and initial project structure |
| M2 | ⚙️ FastAPI Backend Foundation | Running FastAPI app with structured routes, environment configuration, and health check |
| M3 | 📄 Document Upload & Processing Foundation | Upload endpoint, file validation, project-based storage, and document processing foundation |
| M4 | 🗄️ Database Metadata, Indexing & Ingestion Pipeline | MongoDB metadata layer, asset schemas, stores, indexes, upload metadata persistence, processing metadata persistence, and stable ingestion pipeline |
| M5 | 🔎 RAG Core: LLM, Vector Store & Retrieval | LLM factory, vector database factory, embeddings, indexing, semantic search, retrieval, grounded answer generation, citation validation, and RAG Core stabilization |
| M6 | 🐳 Production Deployment & Workers | PostgreSQL/PgVector evolution, SQLAlchemy, Alembic, Docker deployment, provider hardening, workers, schedulers, and production runtime setup |
| M7 | 🛡️ Observability, Security & Agent-Ready Evolution | Monitoring, structured logs, evaluation, security hardening, and preparation for agentic system integration |

---

## 🚦 Current Development Focus

### Current Milestone

Milestone 6 — Production Deployment & Workers

### Latest Completed Branch

Branch 22 — Production Docker Runtime & Observability Foundation

Git branch:

```text
feature/22-production-docker-observability
```

Branch 22 turns the Branch 21 RAG engine into a production-like, observable Docker runtime.

It keeps the existing RAGForge architecture intact: MongoDB remains the current ingestion metadata and chunk store, PostgreSQL/PgVector remains the active production vector backend, Qdrant remains supported as an optional vector backend, and the route/service/provider boundaries introduced in previous branches remain unchanged.

Branch 22 adds a server-ready Docker runtime around the existing application:

```text
Nginx
  ↓
RAGForge FastAPI container
  ↓
MongoDB metadata + chunks
  ↓
PostgreSQL / PgVector
  ↓
Qdrant optional backend
  ↓
Prometheus scraping
  ↓
Grafana dashboards / datasource provisioning
```

The Branch 22 production runtime path is:

```text
Docker Compose production stack
  ↓
ragforge-migrations one-shot service
  ↓
ragforge-api container
  ↓
Nginx reverse proxy
  ↓
Prometheus metrics scraping
  ↓
Grafana datasource provisioning
  ↓
Postgres exporter / Node exporter
```

Branch 22 adds and validates:

- production Docker Compose runtime,
- RAGForge Dockerfile and container entrypoint,
- separate one-shot migration service,
- Nginx reverse proxy configuration,
- Prometheus scraping configuration,
- Grafana datasource provisioning,
- FastAPI Prometheus metrics middleware,
- route-template metrics to avoid high-cardinality raw path labels,
- Prometheus multiprocess collector support,
- PostgreSQL/PgVector monitoring through Postgres exporter,
- Node exporter service,
- production environment examples,
- production Docker runtime documentation,
- static runtime validation script,
- observability test coverage.

Validated result:

```text
Branch 22 static production runtime file validation passed.
Branch 22 production Docker observability validation passed.
Branch 22 observability tests: 2 passed.
Full test suite: 95 passed.
```

### Next Focus

Continue Milestone 6 with server deployment and continuous delivery automation.

The next development focus is:

- Ubuntu server deployment structure,
- deployment user and SSH key strategy,
- server-side secrets handling,
- systemd service supervision,
- firewall hardening,
- GitHub Actions deployment workflow,
- production healthcheck automation,
- rollback and backup scripts,
- HTTPS/TLS deployment hardening,
- Grafana dashboard provisioning and operational validation.

## 📚 Documentation Map Entries

| Document | Purpose |
|---|---|
| [`docs/architecture/backend-architecture.md`](docs/architecture/backend-architecture.md) | Stable backend architecture and long-term design principles |
| [`docs/milestones/milestone-04-database-metadata-indexing/milestone-04-database-metadata-indexing.md`](docs/milestones/milestone-04-database-metadata-indexing/milestone-04-database-metadata-indexing.md) | Milestone 4 metadata and ingestion pipeline overview |
| [`docs/milestones/milestone-04-database-metadata-indexing/branches/branch-13-data-pipeline-enhancements.md`](docs/milestones/milestone-04-database-metadata-indexing/branches/branch-13-data-pipeline-enhancements.md) | Branch 13 implementation details and validation |
| [`docs/milestones/milestone-05-rag-core/milestone-05-rag-core.md`](docs/milestones/milestone-05-rag-core/milestone-05-rag-core.md) | Milestone 5 RAG Core overview |
| [`docs/milestones/milestone-05-rag-core/branches/branch-14-llm-factory.md`](docs/milestones/milestone-05-rag-core/branches/branch-14-llm-factory.md) | Branch 14 LLM Factory implementation details |
| [`docs/milestones/milestone-05-rag-core/branches/branch-15-vector-db-factory-qdrant.md`](docs/milestones/milestone-05-rag-core/branches/branch-15-vector-db-factory-qdrant.md) | Branch 15 Vector DB Factory with Qdrant implementation details |
| [`docs/milestones/milestone-05-rag-core/branches/branch-16-embeddings-indexing.md`](docs/milestones/milestone-05-rag-core/branches/branch-16-embeddings-indexing.md) | Branch 16 Embeddings & Indexing Foundation implementation details |
| [`docs/milestones/milestone-05-rag-core/branches/branch-17-semantic-search.md`](docs/milestones/milestone-05-rag-core/branches/branch-17-semantic-search.md) | Branch 17 Semantic Search implementation details |
| [`docs/milestones/milestone-05-rag-core/branches/branch-18-augmented-answers-with-sources.md`](docs/milestones/milestone-05-rag-core/branches/branch-18-augmented-answers-with-sources.md) | Branch 18 Augmented Answers with Sources implementation details |
| [`docs/milestones/milestone-05-rag-core/branches/branch-19-rag-core-stabilization.md`](docs/milestones/milestone-05-rag-core/branches/branch-19-rag-core-stabilization.md) | Branch 19 RAG Core Stabilization implementation details |
| [`docs/milestones/milestone-06-production-deployment-workers/milestone-06-production-deployment-workers.md`](docs/milestones/milestone-06-production-deployment-workers/milestone-06-production-deployment-workers.md) | Milestone 6 Production Deployment & Workers overview |
| [`docs/milestones/milestone-06-production-deployment-workers/branches/branch-20-postgres-sqlalchemy-alembic-production-layer.md`](docs/milestones/milestone-06-production-deployment-workers/branches/branch-20-postgres-sqlalchemy-alembic-production-layer.md) | Branch 20 PostgreSQL + SQLAlchemy + Alembic production layer implementation details |
| [`docs/milestones/milestone-06-production-deployment-workers/branches/branch-21-pgvector-provider-indexing.md`](docs/milestones/milestone-06-production-deployment-workers/branches/branch-21-pgvector-provider-indexing.md) | Branch 21 PgVector provider implementation, validation, and real RAG test notes |
| [`docs/milestones/milestone-06-production-deployment-workers/branches/branch-22-production-docker-observability.md`](docs/milestones/milestone-06-production-deployment-workers/branches/branch-22-production-docker-observability.md) | Branch 22 production Docker runtime and observability foundation implementation details |
| [`docs/setup/local-development.md`](docs/setup/local-development.md) | Local setup, installation, running commands, and common problems |
| [`docs/setup/postgres-alembic.md`](docs/setup/postgres-alembic.md) | PostgreSQL and Alembic setup and validation notes |
| [`docs/setup/production-docker-runtime.md`](docs/setup/production-docker-runtime.md) | Production Docker runtime, observability stack, and validation commands |
| [`docs/api/endpoints.md`](docs/api/endpoints.md) | API endpoints, request examples, and response examples |

---

## 🧱 Architecture Overview

RAGForge follows a production-oriented FastAPI `src/` architecture with a service-based backend structure.

The stable architecture principle is:

```text
Route → Service → Infrastructure
```

More specifically:

```text
HTTP Request
    ↓
FastAPI Route
    ↓
Service Layer
    ↓
Storage / Database / Vector Database / LLM / Embedding Provider
    ↓
API Response
```

After Branch 13, the document processing flow follows this structure:

```text
documents.py
  ↓
PipelineService
  ↓
DocumentProcessingService
  ↓
ProjectStore / AssetStore / ChunkStore
  ↓
MongoDB
```

After Branch 14 and Branch 15, the RAG Core foundation adds provider-based AI infrastructure:

```text
Application / Route Layer
  ↓
Service Layer
  ├── LLMService
  └── VectorDBService
      ↓
Provider Factories
  ├── LLMProviderFactory
  └── VectorDBProviderFactory
      ↓
Provider Interfaces
  ├── BaseLLMProvider
  └── BaseVectorDBProvider
      ↓
Provider Implementations
  ├── FakeLLMProvider
  ├── OpenAICompatibleLLMProvider
  └── QdrantProvider
```

After Branch 16, the indexing foundation adds the embedding and indexing path:

```text
Indexing Route
  ↓
IndexingService
  ↓
ProjectStore / ChunkStore
  ↓
EmbeddingProviderFactory
  ↓
EmbeddingProvider
  ↓
VectorDBService
  ↓
VectorDBProviderFactory
  ↓
Vector DB Provider
```

After Branch 17, the semantic search path is:

```text
Search Route
  ↓
SemanticSearchService
  ↓
ProjectStore
  ↓
EmbeddingProviderFactory
  ↓
EmbeddingProvider
  ↓
VectorDBService
  ↓
VectorDBProviderFactory
  ↓
Vector DB Provider
  ↓
Ranked Evidence
```

After Branch 18 and Branch 19, the grounded answer path is stabilized with retrieval post-processing and citation validation:

```text
Answers Route
  ↓
RAGAnswerService
  ↓
SemanticSearchService
  ↓
RetrievalPostprocessor
  ↓
RAGContextBuilder
  ↓
RAG Prompt Builder
  ↓
LLMService
  ↓
CitationValidator
  ↓
Answer + Sources + Evidence + Warnings + Diagnostics
```

After Branch 20, the production persistence foundation adds PostgreSQL, SQLAlchemy async ORM, Alembic migrations, repositories, domain records, and a Unit of Work transaction boundary:

```text
Application / Service Layer
  ↓
PostgresSessionManager
  ↓
PostgresUnitOfWork
  ↓
ProjectRepository / AssetRepository / ChunkRepository
  ↓
Domain Records
  ↓
SQLAlchemy ORM Models
  ↓
PostgreSQL / PgVector
```

After Branch 21, PgVector becomes an active vector database backend behind the same provider-neutral vector service used by Qdrant:

```text
VectorDBService
  ↓
VectorDBProviderFactory
  ↓
BaseVectorDBProvider
  ├── QdrantProvider
  └── PgVectorProvider
      ↓
PostgreSQL vector_records table
      ↓
pgvector extension + vector indexes
```

After Branch 22, the production runtime and observability foundation wrap the existing application without changing the RAG Core service boundaries:

```text
Nginx Reverse Proxy
  ↓
RAGForge FastAPI Container
  ↓
Service Layer / Provider Layer
  ↓
MongoDB + PostgreSQL/PgVector + Qdrant
  ↓
Prometheus Metrics Collection
  ↓
Grafana Datasource Provisioning
  ↓
Operational Validation
```

Branch 22 keeps deployment infrastructure outside business logic. Metrics are exposed through a configurable FastAPI observability layer, while Prometheus, Grafana, exporters, and Docker runtime concerns stay in the deployment boundary.

The route stays thin. The orchestration lives in the service layer. Provider-specific implementation details stay behind interfaces. Transaction ownership stays in the Unit of Work layer, not inside repositories.

Full architecture reference:

[`docs/architecture/backend-architecture.md`](docs/architecture/backend-architecture.md)

---

## 🧩 No-Hardcode Architecture Rule

RAGForge follows a strict configuration rule:

```text
.env
  ↓
core/config.py
  ↓
settings
  ↓
factory/service
  ↓
provider / infrastructure boundary
```

Runtime operational values must not be hidden inside services, routes, or provider factories.

Allowed places for defaults:

```text
.env.example
src/ragforge/core/config.py
tests
validation scripts
documentation
```

Not allowed:

```text
services
routes
provider factories
provider-neutral orchestration code
```

Examples of values that must come from configuration:

```text
embedding model
embedding provider
embedding vector size
vector database provider
vector collection name
vector table name
distance metric
provider URL
provider name
LLM model
temperature
timeouts
token limits
answer default limit
answer max context size
debug prompt behavior
PostgreSQL host / port / credentials / pool settings
PgVector index type / index parameters
```

Generic services must not reference provider-specific configuration names such as `QDRANT_COLLECTION_NAME`, `QDRANT_VECTOR_SIZE`, `PGVECTOR_TABLE_NAME`, or `PGVECTOR_INDEX_TYPE`.

Provider-specific settings are allowed only at provider boundaries, such as the provider factory and provider implementation.

Database-specific behavior is allowed at database infrastructure boundaries, such as PostgreSQL session management, SQLAlchemy models, repositories, PgVector provider code, and Alembic migrations.

This keeps RAGForge provider-aware at the boundaries, testable, and ready for future backends such as Qdrant, PgVector, Weaviate, Milvus, Pinecone, or another vector database.

---

## 📦 Project Structure

```text
ragforge/
├── README.md
├── LICENSE
├── requirements.txt
├── requirements_branch22_additions.txt
├── alembic.ini
├── .env.example
├── .gitignore
├── .dockerignore
│
├── docker/
│   ├── docker-compose.yml
│   ├── docker-compose.production.yml
│   ├── .gitignore
│   ├── env/
│   │   ├── .env.app.example
│   │   ├── .env.grafana.example
│   │   ├── .env.mongodb.example
│   │   ├── .env.postgres.example
│   │   └── .env.postgres-exporter.example
│   ├── grafana/
│   │   └── provisioning/
│   │       └── datasources/
│   │           └── prometheus.yml
│   ├── nginx/
│   │   └── default.conf
│   ├── prometheus/
│   │   └── prometheus.yml
│   └── ragforge/
│       ├── Dockerfile
│       └── entrypoint.sh
│
├── migrations/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 20260605_0001_create_postgres_metadata_schema.py
│       └── 20260606_0002_create_pgvector_vector_records.py
│
├── docs/
│   ├── architecture/
│   │   └── backend-architecture.md
│   ├── milestones/
│   │   ├── milestone-03-document-upload/
│   │   ├── milestone-04-database-metadata-indexing/
│   │   ├── milestone-05-rag-core/
│   │   │   ├── milestone-05-rag-core.md
│   │   │   └── branches/
│   │   │       ├── branch-14-llm-factory.md
│   │   │       ├── branch-15-vector-db-factory-qdrant.md
│   │   │       ├── branch-16-embeddings-indexing.md
│   │   │       ├── branch-17-semantic-search.md
│   │   │       ├── branch-18-augmented-answers-with-sources.md
│   │   │       └── branch-19-rag-core-stabilization.md
│   │   └── milestone-06-production-deployment-workers/
│   │       ├── milestone-06-production-deployment-workers.md
│   │       └── branches/
│   │           ├── branch-20-postgres-sqlalchemy-alembic-production-layer.md
│   │           ├── branch-21-pgvector-provider-indexing.md
│   │           └── branch-22-production-docker-observability.md
│   ├── setup/
│   │   ├── local-development.md
│   │   ├── postgres-alembic.md
│   │   └── production-docker-runtime.md
│   └── api/
│       └── endpoints.md
│
├── resources/
├── scripts/
│   └── validation/
│       ├── validate_branch_15_vector_db.py
│       ├── validate_branch_16_indexing.py
│       ├── validate_branch_17_semantic_search.py
│       ├── validate_branch_18_answers.py
│       ├── validate_branch_19_rag_core_stabilization.py
│       ├── validate_branch_20_alembic_state.py
│       ├── validate_branch_20_postgres_production_layer.py
│       ├── validate_branch_21_pgvector_provider.py
│       └── validate_branch_22_production_runtime.py
│
├── storage/
│   └── uploads/
│       └── {project_id}/
│           └── documents/
│
├── tests/
│   ├── branch_21_pgvector/
│   │   ├── test_indexing_service_pgvector_reset.py
│   │   ├── test_pgvector_factory_selection.py
│   │   ├── test_pgvector_index_policy.py
│   │   ├── test_pgvector_provider_contract.py
│   │   ├── test_pgvector_provider_sql_safety.py
│   │   ├── test_pgvector_similarity_scoring.py
│   │   ├── test_pgvector_vector_size_config.py
│   │   ├── test_semantic_search_pgvector_backend.py
│   │   └── test_vector_db_async_contract.py
│   ├── branch_22_observability/
│   │   └── test_metrics_middleware.py
│   ├── test_answer_schemas.py
│   ├── test_embedding_provider_factory.py
│   ├── test_indexing_schemas.py
│   ├── test_llm_factory.py
│   ├── test_llm_service.py
│   ├── test_citation_validator.py
│   ├── test_rag_answer_service.py
│   ├── test_rag_answer_service_stability.py
│   ├── test_rag_context_builder.py
│   ├── test_retrieval_postprocessor.py
│   ├── test_search_schemas.py
│   ├── test_semantic_search_service.py
│   ├── test_vector_db_factory.py
│   ├── test_postgres_model_identity.py
│   ├── test_postgres_package_hygiene.py
│   ├── test_postgres_protocols_do_not_return_orm_tables.py
│   ├── test_postgres_repository_transaction_policy.py
│   ├── test_postgres_unit_of_work_policy.py
│   └── test_postgres_url_builders.py
│
└── src/
    └── ragforge/
        ├── main.py
        ├── core/
        ├── exceptions/
        ├── models/
        │   ├── enums/
        │   └── db_schemes/
        ├── observability/
        │   ├── __init__.py
        │   └── metrics.py
        ├── prompts/
        │   └── rag_answer_prompt.py
        ├── providers/
        │   ├── embedding/
        │   ├── llm/
        │   └── vector_db/
        │       ├── base.py
        │       ├── enums.py
        │       ├── factory.py
        │       ├── schemas.py
        │       └── implementations/
        │           ├── qdrant_provider.py
        │           └── pgvector_provider.py
        ├── routes/
        │   ├── answers.py
        │   ├── documents.py
        │   ├── indexing.py
        │   ├── llm.py
        │   └── search.py
        ├── schemas/
        │   ├── answers.py
        │   ├── document_processing.py
        │   ├── indexing.py
        │   └── search.py
        ├── services/
        │   ├── document_service.py
        │   ├── document_processing_service.py
        │   ├── indexing_service.py
        │   ├── llm_service.py
        │   ├── pipeline_service.py
        │   ├── rag_answer_service.py
        │   ├── rag_context_builder.py
        │   ├── semantic_search_service.py
        │   └── vector_db_service.py
        ├── stores/
        │   ├── mongodb/
        │   └── postgres/
        │       ├── session.py
        │       ├── unit_of_work.py
        │       ├── records.py
        │       ├── models/
        │       └── repositories/
        └── utils/
```

Detailed branch-level file changes belong in the relevant branch document, not in this README.

---

## 🌐 API Documentation

Current API endpoints, request examples, response examples, and testing notes are documented here:

[`docs/api/endpoints.md`](docs/api/endpoints.md)

Swagger UI is available when the server is running:

```text
http://127.0.0.1:8000/docs
```

---

## 🚀 Local Development

Local setup, environment preparation, installation commands, and run instructions are documented here:

[`docs/setup/local-development.md`](docs/setup/local-development.md)

PostgreSQL and Alembic setup details are documented here:

[`docs/setup/postgres-alembic.md`](docs/setup/postgres-alembic.md)

Quick run command:

```bash
uvicorn src.ragforge.main:app --reload --reload-dir src --host 127.0.0.1 --port 8000
```

For real local validation with Docker volumes inside the repository, run without reload or restrict reload directories to avoid file-watcher permission errors:

```bash
uvicorn src.ragforge.main:app --host 127.0.0.1 --port 8000
```

MongoDB, Qdrant, and PostgreSQL/PgVector are launched through the Docker Compose file inside the `docker/` directory:

```bash
docker compose --env-file .env -f docker/docker-compose.yml up -d
```

Check container status:

```bash
docker compose --env-file .env -f docker/docker-compose.yml ps
```

Branch 22 also provides a production-like Docker runtime:

```bash
cp docker/env/.env.app.example docker/env/.env.app
cp docker/env/.env.mongodb.example docker/env/.env.mongodb
cp docker/env/.env.postgres.example docker/env/.env.postgres
cp docker/env/.env.grafana.example docker/env/.env.grafana
cp docker/env/.env.postgres-exporter.example docker/env/.env.postgres-exporter

docker compose -f docker/docker-compose.production.yml up --build -d
docker compose -f docker/docker-compose.production.yml ps
```

Production runtime local endpoints:

```text
RAGForge API direct: http://127.0.0.1:8000/api/v1/health/
Nginx reverse proxy: http://127.0.0.1:8088/api/v1/health/
Prometheus:          http://127.0.0.1:9090
Grafana:             http://127.0.0.1:3000
```

Check Qdrant health:

```bash
curl http://localhost:6333/healthz
```

Check PostgreSQL and PgVector:

```bash
docker exec -it ragforge-postgres psql -U ragforge -d ragforge -c "SELECT version();"
docker exec -it ragforge-postgres psql -U ragforge -d ragforge -c "CREATE EXTENSION IF NOT EXISTS vector;"
docker exec -it ragforge-postgres psql -U ragforge -d ragforge -c "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"
```

Run Alembic migrations:

```bash
alembic -c alembic.ini upgrade head
alembic -c alembic.ini current
```

Expected current head after Branch 21:

```text
20260606_0002 (head)
```

Run validation scripts:

```bash
python scripts/validation/validate_branch_15_vector_db.py
python scripts/validation/validate_branch_16_indexing.py
python scripts/validation/validate_branch_17_semantic_search.py
python scripts/validation/validate_branch_18_answers.py
python scripts/validation/validate_branch_19_rag_core_stabilization.py
python scripts/validation/validate_branch_20_alembic_state.py
python scripts/validation/validate_branch_20_postgres_production_layer.py
python scripts/validation/validate_branch_21_pgvector_provider.py
python scripts/validation/validate_branch_22_production_runtime.py
```

Run tests:

```bash
pytest
```

---

## 🔎 RAG Core Endpoints

### Indexing Endpoint

```http
POST /api/v1/indexing/{project_id}
```

Example request:

```json
{
  "asset_id": null,
  "do_reset": true,
  "batch_size": 32,
  "limit": null,
  "strategy": "simple_chunk",
  "granularity": "chunk",
  "include_results": true
}
```

### Semantic Search Endpoint

```http
POST /api/v1/search/{project_id}
```

Example request:

```json
{
  "query": "PostgreSQL pgvector extension OpenAI embeddings",
  "limit": 5,
  "asset_id": null,
  "min_score": null,
  "include_text": true,
  "include_metadata": true
}
```

With `VECTOR_DB_PROVIDER="pgvector"`, semantic search retrieves from PostgreSQL/PgVector.

With `VECTOR_DB_PROVIDER="qdrant"`, semantic search retrieves from Qdrant.

The same route and service layer are used for both backends.

### Stabilized Answer Endpoint

```http
POST /api/v1/answers/{project_id}
```

Example request:

```json
{
  "question": "What is RAGForge?",
  "limit": 5,
  "asset_id": null,
  "min_score": null,
  "include_sources": true,
  "include_evidence": true,
  "include_debug_prompt": false
}
```

The answer endpoint returns:

```text
rag_answer_success
answer
sources
evidence
llm_model
retrieval_count
debug_prompt
warnings
retrieval_diagnostics
citation_validation
```

The fake LLM provider returns a deterministic fake response for local validation. With a real OpenAI-compatible provider, the same endpoint generates a real grounded answer from retrieved evidence.

Branch 19 keeps debug prompts hidden by default and adds response stability fields so clients can inspect retrieval behavior and citation safety without changing the public endpoint.

Branch 21 validates that the same answer endpoint can run on PgVector-backed retrieval.

---

## 🐘 PostgreSQL / PgVector Configuration

Branch 20 introduces PostgreSQL as the production persistence foundation.

Branch 21 activates PgVector as a real vector database provider behind the RAG runtime path.

PostgreSQL runtime configuration:

```env
POSTGRES_USER=ragforge
POSTGRES_PASSWORD=ragforge_password_change_me
POSTGRES_DB=ragforge
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_ECHO=false
POSTGRES_POOL_SIZE=5
POSTGRES_MAX_OVERFLOW=10
POSTGRES_POOL_TIMEOUT=30
POSTGRES_POOL_RECYCLE=1800
```

When the application runs from the host or WSL environment, `POSTGRES_HOST=localhost` and `POSTGRES_PORT=5433` are used.

When the application later runs inside Docker Compose, the internal service name and container port can be used:

```env
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
```

PgVector provider configuration:

```env
VECTOR_DB_PROVIDER="pgvector"
VECTOR_DB_COLLECTION_NAME="ragforge_chunks"
VECTOR_DB_VECTOR_SIZE=1536
VECTOR_DB_DISTANCE="cosine"

PGVECTOR_TABLE_NAME="vector_records"
PGVECTOR_DISTANCE="cosine"
PGVECTOR_INDEX_TYPE="hnsw"
PGVECTOR_INDEX_VECTOR_TYPE="vector"
PGVECTOR_HNSW_M=16
PGVECTOR_HNSW_EF_CONSTRUCTION=64
PGVECTOR_HNSW_EF_SEARCH=40
PGVECTOR_IVFFLAT_LISTS=100
PGVECTOR_IVFFLAT_PROBES=10
PGVECTOR_INDEX_MIN_RECORDS=0
PGVECTOR_AUTO_CREATE_INDEX=true
PGVECTOR_CREATE_EXTENSION_ON_STARTUP=true
```

Branch 21 validates PgVector with:

```bash
python scripts/validation/validate_branch_21_pgvector_provider.py
pytest tests/branch_21_pgvector -q
```

---

## ⚙️ RAG Core Configuration

Generic vector indexing configuration:

```env
VECTOR_DB_PROVIDER="pgvector"
VECTOR_DB_COLLECTION_NAME="ragforge_chunks"
VECTOR_DB_VECTOR_SIZE=1536
VECTOR_DB_DISTANCE="cosine"
```

Qdrant provider configuration:

```env
VECTOR_DB_PROVIDER="qdrant"
QDRANT_MODE="server"
QDRANT_URL="http://localhost:6333"
QDRANT_API_KEY=""
QDRANT_LOCAL_PATH="storage/vector_db/qdrant"
QDRANT_PREFER_GRPC=false
```

Embedding configuration:

```env
EMBEDDING_PROVIDER="openai_compatible"
EMBEDDING_MODEL="text-embedding-3-small"
EMBEDDING_VECTOR_SIZE=1536
EMBEDDING_BATCH_SIZE=32
FAKE_EMBEDDING_MODEL="fake-embedding-model"

EMBEDDING_OPENAI_API_KEY=""
EMBEDDING_OPENAI_BASE_URL="https://api.openai.com/v1"
```

For local fake validation:

```env
EMBEDDING_PROVIDER="fake"
```

Semantic search configuration:

```env
SEARCH_DEFAULT_LIMIT=5
SEARCH_MAX_LIMIT=20
# SEARCH_MIN_SCORE=
SEARCH_INCLUDE_TEXT_DEFAULT=true
SEARCH_INCLUDE_METADATA_DEFAULT=true
```

RAG answer configuration:

```env
RAG_ANSWER_DEFAULT_LIMIT=5
RAG_ANSWER_MAX_CONTEXT_CHARS=8000
RAG_ANSWER_INCLUDE_SOURCES_DEFAULT=true
RAG_ANSWER_INCLUDE_EVIDENCE_DEFAULT=true
RAG_ANSWER_DEBUG_PROMPT_DEFAULT=false
```

Retrieval stabilization configuration:

```env
RAG_RETRIEVAL_CANDIDATE_LIMIT=30
RAG_RETRIEVAL_MIN_SCORE=0.25
RAG_MAX_CHUNKS_PER_ASSET=3
RAG_ENABLE_SOURCE_DEDUP=true
RAG_ENABLE_DOMINANT_ASSET=true
RAG_DOMINANT_ASSET_SCORE_GAP=0.08
RAG_DOMINANT_ASSET_MIN_CHUNKS=2
RAG_ENABLE_CITATION_VALIDATION=true
```

LLM configuration:

```env
LLM_PROVIDER="openai_compatible"
LLM_DEFAULT_MODEL="gpt-4o-mini"
LLM_TEMPERATURE=0.2
LLM_MAX_OUTPUT_TOKENS=512
LLM_TIMEOUT_SECONDS=60

OPENAI_API_KEY=""
OPENAI_BASE_URL="https://api.openai.com/v1"
```

For local fake validation:

```env
LLM_PROVIDER="fake"
LLM_DEFAULT_MODEL="fake-ragforge-model"
```

Do not commit private `.env` files or API keys.

---

## 🐳 Production Runtime & Observability Configuration

Branch 22 adds a production-like Docker runtime and Prometheus-compatible application metrics.

Metrics configuration:

```env
METRICS_ENABLED=true
METRICS_PATH=/metrics
METRICS_INCLUDE_IN_SCHEMA=false
```

Production Docker runtime environment examples are stored in:

```text
docker/env/.env.app.example
docker/env/.env.mongodb.example
docker/env/.env.postgres.example
docker/env/.env.grafana.example
docker/env/.env.postgres-exporter.example
```

The production Compose stack is defined in:

```text
docker/docker-compose.production.yml
```

The stack includes:

```text
ragforge-migrations
ragforge-api
nginx
mongodb
postgres
qdrant
prometheus
grafana
postgres-exporter
node-exporter
```

The observability layer exposes application-level HTTP metrics such as request count, request duration, in-progress requests, and exception count. Route-template labels are used instead of raw dynamic URL paths to avoid high-cardinality metrics.

Branch 22 keeps deployment concerns separated from RAG Core behavior. Metrics, Docker services, Prometheus, Grafana, exporters, and reverse proxy configuration live at the runtime boundary.

---

## 🧪 Branch 21 Real RAG Test Flow

Branch 21 was validated through the real runtime API using Postman and curl.

The tested path was:

```text
Upload document
  ↓
Process document into MongoDB chunks
  ↓
Index chunks with OpenAI text-embedding-3-small
  ↓
Store vectors in PostgreSQL / pgvector
  ↓
Search with PgVector-backed semantic retrieval
  ↓
Generate an answer with gpt-4o-mini
  ↓
Validate citations
```

Example Postman/curl endpoint sequence:

```text
GET  /api/v1/health/
POST /api/v1/documents/upload/{project_id}
POST /api/v1/documents/process/{project_id}
POST /api/v1/indexing/{project_id}
POST /api/v1/search/{project_id}
POST /api/v1/answers/{project_id}
```

Expected successful answer response includes:

```text
signal = rag_answer_success
embedding_model = text-embedding-3-small
embedding_provider = openai_compatible
llm_model = gpt-4o-mini
retrieval_count > 0
citation_validation.invalid_source_numbers = []
```

A validated answer can use a README source to explain that RAGForge is a production-oriented RAG backend platform, designed as a modular foundation for production-ready RAG systems and broader agentic system architecture.

---

## 🌿 Development Workflow

RAGForge follows a professional GitHub workflow:

```text
Milestone → Issue → Branch → Pull Request → Merge
```

Each branch should focus on one clear responsibility.

Branch numbering is global across the project.

Examples:

```text
Branch 9  → Docker MongoDB Motor Infrastructure
Branch 10 → Asset Metadata Schemes & Stores
Branch 11 → MongoDB Metadata Indexes & Auth
Branch 12 → Upload and Processing Metadata Persistence
Branch 13 → Data Pipeline Enhancements
Branch 14 → LLM Factory
Branch 15 → Vector DB Factory with Qdrant
Branch 16 → Embeddings & Indexing Foundation
Branch 17 → Semantic Search
Branch 18 → Augmented Answers with Sources
Branch 19 → RAG Core Stabilization
Branch 20 → PostgreSQL + SQLAlchemy + Alembic Production Layer
Branch 21 → PgVector Vector Database Provider
Branch 22 → Production Docker Runtime & Observability Foundation
```

Documentation rule:

```text
README.md
= stable public landing page

docs/architecture/
= stable architecture

docs/milestones/
= milestone and branch implementation history

docs/api/
= endpoint details

docs/setup/
= setup and run instructions
```

The README should stay stable.

Branch-specific implementation details should be added to the relevant branch `.md` file.

---

## 🧠 Engineering Principles

RAGForge follows these principles:

- keep routes thin,
- move business logic to services,
- centralize configuration in `core/config.py`,
- use controlled response signals,
- use provider interfaces for replaceable external systems,
- avoid hidden hardcoded operational values in services and factories,
- keep generic services provider-neutral,
- keep provider-specific settings at provider boundaries,
- keep database transactions owned by Unit of Work boundaries,
- keep repositories free from hidden commits,
- keep ORM models behind domain records when returning data from repository contracts,
- keep Alembic migrations aligned with ORM models,
- keep runtime data outside source code,
- keep uploaded files out of Git,
- do not commit private `.env` files,
- do not expose internal absolute paths,
- keep each branch focused on one responsibility,
- use one branch identifier everywhere: Git branch, issue, PR, and documentation,
- document implementation details in milestone branch files,
- treat metadata as a first-class part of modern RAG architecture,
- link every chunk to its source asset for traceability and future citations,
- return source-ready evidence before answer generation,
- generate grounded answers only from retrieved evidence,
- post-process retrieval before prompt construction,
- validate and sanitize generated citations,
- return retrieval diagnostics for answer observability,
- keep answer generation separate from retrieval,
- keep prompt construction separate from orchestration,
- hide debug prompts by default,
- keep pipeline orchestration reusable for future workers and agentic layers,
- keep vector database providers swappable through configuration,
- keep PgVector and Qdrant behind the same vector provider contract,
- keep production runtime concerns outside RAG Core business logic,
- expose operational metrics through a configurable observability boundary,
- avoid high-cardinality metric labels by using route templates,
- keep Docker, Prometheus, Grafana, and reverse proxy concerns in deployment/runtime files.

---

## ✅ Current Stable Backend Capability

At the end of Branch 22, RAGForge can:

```text
Upload document
  ↓
Persist project and asset metadata
  ↓
Process one asset or all project assets
  ↓
Extract and split document content
  ↓
Persist DataChunk records in MongoDB
  ↓
Update asset processing status
  ↓
Generate embeddings for stored chunks
  ↓
Index vectors into Qdrant or PostgreSQL/PgVector
  ↓
Mark chunks as embedded
  ↓
Search indexed vectors by user query
  ↓
Return ranked evidence chunks with source metadata
  ↓
Post-process retrieved evidence
  ↓
Apply retrieval quality policies such as score threshold, source deduplication, max chunks per asset, and dominant asset selection
  ↓
Build source-numbered context
  ↓
Generate a grounded answer through LLMService
  ↓
Validate and sanitize citations
  ↓
Return answer, sources, evidence, model, retrieval count, warnings, diagnostics, and citation validation
```

RAGForge also has:

```text
LLM provider layer
  ↓
Fake and OpenAI-compatible providers
  ↓
LLM service
  ↓
LLM generation endpoint
```

And:

```text
VectorDBService
  ↓
VectorDBProviderFactory
  ↓
BaseVectorDBProvider
  ├── QdrantProvider
  └── PgVectorProvider
```

And:

```text
EmbeddingProviderFactory
  ↓
BaseEmbeddingProvider
  ↓
FakeEmbeddingProvider / OpenAICompatibleEmbeddingProvider
  ↓
IndexingService
  ↓
Qdrant or PgVector vector indexing
```

And:

```text
RAGAnswerService
  ↓
SemanticSearchService
  ↓
RetrievalPostprocessor
  ↓
RAGContextBuilder
  ↓
RAG prompt builder
  ↓
LLMService
  ↓
CitationValidator
  ↓
Grounded answer with structured sources, warnings, diagnostics, and citation validation
```

And:

```text
PostgresSessionManager
  ↓
Async SQLAlchemy session factory
  ↓
PostgresUnitOfWork
  ↓
ProjectRepository / AssetRepository / ChunkRepository
  ↓
Domain records
  ↓
SQLAlchemy ORM models
  ↓
Alembic-managed PostgreSQL schema
  ↓
PostgreSQL / PgVector Docker service
```

And:

```text
Production Docker Runtime
  ↓
Nginx reverse proxy
  ↓
RAGForge API container
  ↓
One-shot migration service
  ↓
MongoDB / PostgreSQL-PgVector / Qdrant services
  ↓
Prometheus application and infrastructure scraping
  ↓
Grafana datasource provisioning
  ↓
Static validation and observability tests
```

Supported `/process/{project_id}` modes from the ingestion pipeline:

```text
all_project_file_assets
single_asset_by_id
single_asset_by_filename
```

Supported RAG Core endpoints now include:

```text
POST /api/v1/llm/generate
POST /api/v1/indexing/{project_id}
POST /api/v1/search/{project_id}
POST /api/v1/answers/{project_id}
```

---

## ✅ Branch 19 Validation Result

Branch 19 validation confirms the stabilized RAG Core v1 flow.

The validated end-to-end test flow is:

```text
Upload
  ↓
Process
  ↓
Index
  ↓
Search
  ↓
Post-process retrieval
  ↓
Answer
  ↓
Validate citations
```

The answer response includes:

```text
rag_answer_success
answer
sources
evidence
llm_model
retrieval_count
debug_prompt = null by default
warnings
retrieval_diagnostics
citation_validation
```

Branch 19 stabilization confirms:

```text
Retrieval can fetch candidates before final filtering.
Retrieval post-processing controls final evidence quality.
Answer generation stays separated from retrieval.
Prompt construction stays isolated.
Citation validation can sanitize invalid source references.
Warnings can explain answer-level safety corrections.
Diagnostics can expose retrieval behavior for debugging and evaluation.
The answer endpoint remains backward-compatible with Branch 18 clients.
```

Architecture audit:

```text
No controller pattern added.
No direct vector database coupling in the answer route/service.
No direct concrete LLM provider coupling in the answer route/service.
No hidden settings fallback in the Branch 19 answer service path.
Retrieval post-processing stays isolated from semantic search.
Citation validation stays isolated from LLM generation.
```

---

## ✅ Branch 20 Validation Result

Branch 20 validation confirms the PostgreSQL production persistence foundation.

Validated commands:

```bash
python -m compileall src/ragforge migrations scripts/validation tests
python scripts/validation/validate_branch_20_alembic_state.py
python scripts/validation/validate_branch_20_postgres_production_layer.py
pytest
```

Validated result:

```text
Branch 20 Alembic state validation passed.
Branch 20 PostgreSQL production-layer validation passed.
Full test suite passed.
```

Branch 20 confirms:

```text
PostgreSQL / PgVector container runs successfully.
PgVector extension is available.
Alembic can upgrade the database to the current head revision.
The PostgreSQL production-layer validation script passes.
Repository tests confirm repositories do not commit.
Unit of Work tests confirm commit and rollback ownership.
Protocol tests confirm repository contracts return domain records, not ORM tables.
URL builder tests confirm safe runtime and Alembic database URL construction.
Package hygiene tests confirm cache files are not tracked.
The full test suite passes.
```

Architecture audit:

```text
No transaction ownership hidden inside repositories.
No ORM table leakage in repository protocols.
No hardcoded PostgreSQL URL construction in runtime code.
Runtime and Alembic share the same URL-building logic.
Alembic migration and ORM models are aligned.
MongoDB ingestion remains stable while PostgreSQL production persistence is introduced safely.
```

---

## ✅ Branch 21 Validation Result

Branch 21 validation confirms the PgVector vector database provider and real runtime integration.

Validated commands:

```bash
docker compose --env-file .env -f docker/docker-compose.yml up -d
docker compose --env-file .env -f docker/docker-compose.yml ps
alembic -c alembic.ini upgrade head
alembic -c alembic.ini current
python -m compileall src/ragforge migrations scripts/validation tests
python scripts/validation/validate_branch_21_pgvector_provider.py
pytest tests/branch_21_pgvector -q
pytest -q
```

Expected Alembic head:

```text
20260606_0002 (head)
```

Validated PgVector provider output:

```text
PostgreSQL ping succeeded.
PgVector extension exists.
vector_records table exists.
Configured PgVector index exists.
PgVector insert_many succeeded.
PgVector search_by_vector succeeded.
Branch 21 PgVector provider validation passed.
```

Validated test result:

```text
Branch 21 tests passed.
Full test suite passed.
```

Real Postman-based RAG validation confirmed:

```text
signal = rag_answer_success
embedding_model = text-embedding-3-small
embedding_provider = openai_compatible
llm_model = gpt-4o-mini
retrieval_count > 0
citation_validation.invalid_source_numbers = []
```

Branch 21 confirms:

```text
PgVector is an active vector database backend, not only a Docker dependency.
Qdrant remains supported behind the same provider-neutral service boundary.
MongoDB remains the current ingestion metadata and chunk store.
PostgreSQL/PgVector stores searchable vectors in the vector_records table.
Indexing can insert OpenAI embedding vectors into PgVector.
Semantic search can retrieve ranked evidence from PgVector.
The answer endpoint can generate grounded answers from PgVector-backed retrieval.
Citation validation works with PgVector-backed evidence.
Provider selection works through VECTOR_DB_PROVIDER.
```

Architecture audit:

```text
No route changes required to switch Qdrant/PgVector.
No service-layer hardcoding of PgVector-specific settings.
Provider-specific logic stays inside provider/factory boundaries.
The vector database contract is async across providers.
Qdrant compatibility is preserved after the async contract upgrade.
PgVector SQL behavior is covered by safety and contract tests.
Vector size is controlled by EMBEDDING_VECTOR_SIZE with optional equality guards.
```

---

## ✅ Branch 22 Validation Result

Branch 22 validation confirms the production Docker runtime and observability foundation.

Validated commands:

```bash
python scripts/validation/validate_branch_22_production_runtime.py
pytest tests/branch_22_observability -q
pytest -q
```

Validated output:

```text
Branch 22 static production runtime file validation passed.
Branch 22 production Docker observability validation passed.
2 passed
95 passed
```

Branch 22 confirms:

```text
The production Docker Compose runtime is present and statically validated.
The RAGForge API has a production Dockerfile and entrypoint.
The API container can be orchestrated with MongoDB, PostgreSQL/PgVector, Qdrant, Nginx, Prometheus, Grafana, Postgres exporter, and Node exporter.
The migration service is separated from the long-running API container.
FastAPI metrics middleware is available through a configurable metrics boundary.
Prometheus route-template metrics avoid high-cardinality raw path labels.
Prometheus multiprocess collector support is prepared for multi-worker runtime.
Grafana datasource provisioning is present.
Nginx reverse proxy configuration is present.
Branch 21 PgVector and Qdrant provider compatibility is preserved.
The existing RAG Core test suite remains stable.
```

Architecture audit:

```text
No GitHub Actions or VPS automation is mixed into Branch 22.
No RAG Core behavior is changed by deployment infrastructure.
No provider-specific deployment behavior leaks into generic services.
No real secrets are committed.
Production runtime files stay inside the Docker and setup documentation boundary.
Observability is added as an application boundary, not as route/service business logic.
The full test suite remains green after adding runtime and observability infrastructure.
```

---

## 👤 Author

**Dameur Mounir**

AI engineer and system builder focused on production-grade RAG, agentic AI systems, vector databases, observability, and deployable AI architectures.

My objective is to build practical, robust, and scalable AI systems that can evolve from learning projects into real products, client solutions, and future agentic platforms.
