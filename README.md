# 🛠️ RAGForge

**RAGForge** is a production-oriented **Retrieval-Augmented Generation (RAG)** backend platform built step by step with real software engineering practices.

The project starts from a clean FastAPI backend and progressively evolves toward document ingestion, project-based storage, metadata management, text extraction, chunking, LLM integration, vector databases, embeddings, vector search, RAG answer generation, background workers, observability, and production deployment.

RAGForge is not a notebook demo. It is designed as a long-term AI engineering project focused on building a clean, scalable, and professional backend architecture.

---

## 🎯 Project Vision

RAGForge aims to become a modular foundation for building production-ready RAG systems.

The objective is to master the full engineering path from a basic backend service to a production-ready AI platform that can later be reused by applications, websites, internal tools, or agent systems as a reliable knowledge backend.

---

## 🧠 Knowledge-Oriented RAG Direction

RAGForge is built with the understanding that **RAG is not dead**.

What is becoming obsolete is **naive RAG**: systems that only split documents into chunks, retrieve a few similar passages, and pass them directly to an LLM without strong metadata, structure, provenance, indexing, or workflow control.

RAGForge follows a more modern **knowledge-oriented RAG direction**.

The goal is to evolve from simple document retrieval toward a production-grade knowledge backend where every source is tracked as an asset, every extracted chunk is linked to its origin, metadata is persisted, indexes are prepared, and future retrieval can support grounded answers, citations, semantic search, and agent-ready knowledge access.

The architectural direction is:

```text
Project
  ↓
Asset
  ↓
DataChunk
  ↓
Metadata Indexing
  ↓
Semantic Search
  ↓
Grounded / Augmented Answer
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
| M5 | 🔎 RAG Core: LLM, Vector Store & Retrieval | LLM factory, vector database factory, embeddings, semantic search, retrieval, and grounded answer generation |
| M6 | 🐳 Production Deployment & Workers | Docker deployment, PostgreSQL/PgVector evolution, Redis, Celery workers, schedulers, and production runtime setup |
| M7 | 🛡️ Observability, Security & Agent-Ready Evolution | Monitoring, structured logs, evaluation, security hardening, and preparation for agentic system integration |

---

## 🚦 Current Development Focus

### Current Milestone

Milestone 5 — RAG Core: LLM, Vector Store & Retrieval

### Current Branch

Branch 15 — Vector DB Factory with Qdrant

Git branch:

```text
feature/15-vector-db-factory-qdrant
```

Branch 15 introduces the provider-neutral vector database layer.

It adds:

- Qdrant Docker service
- vector DB provider enum
- vector DB record and search schemas
- vector DB exceptions
- base vector DB provider interface
- Qdrant provider implementation
- vector DB provider factory
- vector DB service
- validation script with fake vectors
- factory tests

Branch 15 uses:

```text
qdrant-client==1.18.0
QdrantClient.query_points()
```

Branch 15 does not introduce embedding generation, MongoDB chunk indexing, semantic search endpoints, grounded answers, or agents.

---

## Documentation Map Entries

| Document | Purpose |
|---|---|
| [`docs/milestones/milestone-05-rag-core/milestone-05-rag-core.md`](docs/milestones/milestone-05-rag-core/milestone-05-rag-core.md) | Milestone 5 RAG Core overview |
| [`docs/milestones/milestone-05-rag-core/branches/branch-14-llm-factory.md`](docs/milestones/milestone-05-rag-core/branches/branch-14-llm-factory.md) | Branch 14 LLM Factory implementation notes |
| [`docs/milestones/milestone-05-rag-core/branches/branch-15-vector-db-factory-qdrant.md`](docs/milestones/milestone-05-rag-core/branches/branch-15-vector-db-factory-qdrant.md) | Branch 15 Vector DB Factory with Qdrant implementation notes |

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
Storage / Database / Vector Database / LLM
    ↓
API Response
```

After Branch 13, the document processing flow follows this cleaner structure:

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

The route stays thin. The orchestration lives in the service layer. Provider-specific implementation details stay behind interfaces.

Full architecture reference:

[`docs/architecture/backend-architecture.md`](docs/architecture/backend-architecture.md)

---

## 📦 Project Structure

```text
ragforge/
├── README.md
├── LICENSE
├── requirements.txt
├── .env.example
├── .gitignore
│
├── docker/
│   └── docker-compose.yml
│
├── docs/
│   ├── architecture/
│   │   └── backend-architecture.md
│   ├── milestones/
│   │   ├── milestone-03-document-upload/
│   │   ├── milestone-04-database-metadata-indexing/
│   │   └── milestone-05-rag-core/
│   │       ├── milestone-05-rag-core.md
│   │       └── branches/
│   │           ├── branch-14-llm-factory.md
│   │           └── branch-15-vector-db-factory-qdrant.md
│   ├── setup/
│   │   └── local-development.md
│   └── api/
│       └── endpoints.md
│
├── resources/
├── scripts/
│   └── validation/
│       └── validate_branch_15_vector_db.py
├── storage/
│   └── uploads/
│       └── {project_id}/
│           └── documents/
│
├── tests/
│   └── test_vector_db_factory.py
│
└── src/
    └── ragforge/
        ├── main.py
        ├── core/
        ├── exceptions/
        ├── models/
        │   ├── enums/
        │   └── db_schemes/
        ├── providers/
        │   ├── llm/
        │   └── vector_db/
        │       ├── base.py
        │       ├── enums.py
        │       ├── exceptions.py
        │       ├── factory.py
        │       ├── schemas.py
        │       └── implementations/
        │           └── qdrant_provider.py
        ├── routes/
        │   └── documents.py
        ├── schemas/
        │   └── document_processing.py
        ├── services/
        │   ├── document_service.py
        │   ├── document_processing_service.py
        │   ├── llm_service.py
        │   ├── pipeline_service.py
        │   └── vector_db_service.py
        ├── stores/
        │   └── mongodb/
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

Quick run command:

```bash
uvicorn src.ragforge.main:app --reload --reload-dir src --host 127.0.0.1 --port 8000
```

MongoDB and Qdrant are launched through the Docker Compose file inside the `docker/` directory:

```bash
docker compose --env-file .env -f docker/docker-compose.yml up -d
```

Check container status:

```bash
docker compose --env-file .env -f docker/docker-compose.yml ps
```

Check Qdrant health:

```bash
curl http://localhost:6333/healthz
```

Run the Branch 15 vector database validation script:

```bash
python scripts/validation/validate_branch_15_vector_db.py
```

---

## 📚 Documentation Map

| Document | Purpose |
|---|---|
| [`docs/architecture/backend-architecture.md`](docs/architecture/backend-architecture.md) | Stable backend architecture and long-term design principles |
| [`docs/milestones/`](docs/milestones/) | All milestone overviews, branch plans, and implementation history |
| [`docs/milestones/milestone-04-database-metadata-indexing/milestone-04-database-metadata-indexing.md`](docs/milestones/milestone-04-database-metadata-indexing/milestone-04-database-metadata-indexing.md) | Milestone 4 metadata and ingestion pipeline overview |
| [`docs/milestones/milestone-04-database-metadata-indexing/branches/branch-13-data-pipeline-enhancements.md`](docs/milestones/milestone-04-database-metadata-indexing/branches/branch-13-data-pipeline-enhancements.md) | Branch 13 implementation details and validation |
| [`docs/milestones/milestone-05-rag-core/milestone-05-rag-core.md`](docs/milestones/milestone-05-rag-core/milestone-05-rag-core.md) | Milestone 5 RAG Core overview |
| [`docs/milestones/milestone-05-rag-core/branches/branch-14-llm-factory.md`](docs/milestones/milestone-05-rag-core/branches/branch-14-llm-factory.md) | Branch 14 LLM Factory implementation details |
| [`docs/milestones/milestone-05-rag-core/branches/branch-15-vector-db-factory-qdrant.md`](docs/milestones/milestone-05-rag-core/branches/branch-15-vector-db-factory-qdrant.md) | Branch 15 Vector DB Factory with Qdrant implementation details |
| [`docs/api/endpoints.md`](docs/api/endpoints.md) | API endpoints, request examples, and response examples |
| [`docs/setup/local-development.md`](docs/setup/local-development.md) | Local setup, installation, running commands, and common problems |

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

- keep routes thin
- move business logic to services
- centralize configuration in `core/config.py`
- use controlled response signals
- use provider interfaces for replaceable external systems
- keep runtime data outside source code
- keep uploaded files out of Git
- do not commit private `.env` files
- do not expose internal absolute paths
- keep each branch focused on one responsibility
- use one branch identifier everywhere: Git branch, issue, PR, and documentation
- document implementation details in milestone branch files
- treat metadata as a first-class part of modern RAG architecture
- link every chunk to its source asset for traceability and future citations
- keep pipeline orchestration reusable for future workers and agentic layers

---

## ✅ Current Stable Backend Capability

At the end of Branch 15, RAGForge can:

```text
Upload document
  ↓
Persist project and asset metadata
  ↓
Process one asset or all project assets
  ↓
Extract and split document content
  ↓
Persist DataChunk records
  ↓
Update asset processing status
  ↓
Return a structured pipeline report
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

And now:

```text
VectorDBService
  ↓
VectorDBProviderFactory
  ↓
BaseVectorDBProvider
  ↓
QdrantProvider
  ↓
Qdrant Docker service
```

Branch 15 validates:

- Qdrant connection,
- collection creation,
- single vector insertion,
- batch vector insertion,
- vector similarity search using `query_points()`,
- validation collection cleanup.

Supported `/process/{project_id}` modes from the ingestion pipeline:

```text
all_project_file_assets
single_asset_by_id
single_asset_by_filename
```

This prepares RAGForge for Branch 16, where MongoDB chunks will be embedded and indexed into Qdrant.

---

## 👤 Author

**Dameur Mounir**

AI engineer and system builder focused on production-grade RAG, agentic AI systems, vector databases, observability, and deployable AI architectures.

My objective is to build practical, robust, and scalable AI systems that can evolve from learning projects into real products, client solutions, and future agentic platforms.
