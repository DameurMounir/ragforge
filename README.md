# 🛠️ RAGForge

**RAGForge** is a production-oriented **Retrieval-Augmented Generation (RAG)** backend platform built step by step with real software engineering practices.

The project starts from a clean FastAPI backend and progressively evolves toward document ingestion, project-based storage, metadata management, text extraction, chunking, embeddings, vector search, RAG answer generation, background workers, and production deployment.

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
| M1 | 🧱 Project Bootstrap & Environment | Repository, environment, Git workflow, README, and initial structure |
| M2 | ⚙️ FastAPI Backend Foundation | Running FastAPI app with structured routes, env config, and health check |
| M3 | 📄 Document Upload & Processing | Upload endpoint, file validation, project storage, and document ingestion foundation |
| M4 | 🗄️ Database Metadata & Indexing | MongoDB metadata layer, asset schemes, stores, metadata indexes, and persistence foundation |
| M5 | 🔁 Data Pipeline Checkpoint | Stable extraction, chunking, and ingestion pipeline |
| M6 | 🔎 RAG Core | Embeddings, vector search, retrieval, and grounded answer generation |
| M7 | 🐳 Production Deployment & Workers | Docker, PostgreSQL, Qdrant/PgVector, Redis, workers, monitoring, and deployment |

---

## 🚦 Current Development Focus

Current branch details are documented outside the README to keep this file stable.

### Current Branch

[`Branch 11 — MongoDB Metadata Indexes & Auth`](docs/milestones/milestone-04-database-metadata-indexing/branches/branch-11-mongodb-metadata-indexes-auth.md)

Git branch:

```text
feature/11-mongodb-metadata-indexes-auth
```

### Milestone Overview

[`Milestone 4 — Database Metadata & Indexing`](docs/milestones/milestone-04-database-metadata-indexing/milestone-04-database-metadata-indexing.md)


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

The architecture document is stable and should not be rewritten for every branch.

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
├── docs/
│   ├── architecture/
│   │   └── backend-architecture.md
│   ├── milestones/
│   │   ├── milestone-03-document-upload/
│   │   │   ├── milestone-03-document-upload.md
│   │   │   └── branches/
│   │   └── milestone-04-database-metadata-indexing/
│   │       ├── milestone-04-database-metadata-indexing.md
│   │       └── branches/
│   │           └── branch-10-asset-metadata-store.md
│   ├── setup/
│   │   └── local-development.md
│   └── api/
│       └── endpoints.md
│
├── resources/
├── storage/
│   └── uploads/
│       └── {project_id}/
│           └── documents/
│
├── tests/
│
└── src/
    └── ragforge/
        ├── main.py
        ├── core/
        ├── routes/
        ├── services/
        ├── models/
        │   ├── enums/
        │   └── db_schemes/
        ├── stores/
        │   └── mongodb/
        ├── schemas/
        ├── utils/
        └── exceptions/
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
uvicorn src.ragforge.main:app --reload --host 127.0.0.1 --port 8000
```

---

## 📚 Documentation Map

| Document | Purpose |
|---|---|
| [`docs/architecture/backend-architecture.md`](docs/architecture/backend-architecture.md) | Stable backend architecture and long-term design principles |
| [`docs/milestones/`](docs/milestones/) | All milestone overviews, branch plans, and implementation history |
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

Example:

```text
Branch 9  → Docker MongoDB Motor Infrastructure
Branch 10 → Asset Metadata Schemes & Stores
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
- keep runtime data outside source code
- keep uploaded files out of Git
- do not commit private `.env` files
- do not expose internal absolute paths
- keep each branch focused on one responsibility
- use one branch identifier everywhere: Git branch, issue, PR, and documentation
- document implementation details in milestone branch files
- treat metadata as a first-class part of modern RAG architecture
- link every chunk to its source asset for traceability and future citations

---

## 👤 Author

**Dameur Mounir**

AI engineer and system builder focused on production-grade RAG, agentic AI systems, vector databases, observability, and deployable AI architectures.

My objective is to build practical, robust, and scalable AI systems that can evolve from learning projects into real products, client solutions, and future agentic platforms.
