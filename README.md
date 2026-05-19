# 🛠️ RAGForge

**RAGForge** is a production-oriented **Retrieval-Augmented Generation (RAG)** backend platform built step by step with real software engineering practices.

The project starts from a clean FastAPI backend and progressively evolves toward document ingestion, project-based storage, metadata management, text extraction, chunking, embeddings, vector search, RAG answer generation, background workers, and production deployment.

RAGForge is not a notebook demo. It is designed as a long-term AI engineering project focused on building a clean, scalable, and professional backend architecture.

---

## 🎯 Project Vision

RAGForge aims to become a modular foundation for building production-ready RAG systems.

The objective is to master the full engineering path from a basic backend service to a production-ready AI platform that can later be reused by applications, websites, internal tools, or agent systems as a reliable knowledge backend.

---

## 🧭 7-Milestone Roadmap

| Milestone | Focus | Expected Result |
|---|---|---|
| M1 | 🧱 Project Bootstrap & Environment | Repository, environment, Git workflow, README, and initial structure |
| M2 | ⚙️ FastAPI Backend Foundation | Running FastAPI app with structured routes, env config, and health check |
| M3 | 📄 Document Upload & Processing | Upload endpoint, file validation, project storage, and document ingestion foundation |
| M4 | 🗄️ Database & Document Models | Store projects, documents, metadata, chunks, and processing status |
| M5 | 🔁 Data Pipeline Checkpoint | Stable extraction, chunking, and ingestion pipeline |
| M6 | 🔎 RAG Core | Embeddings, vector search, retrieval, and grounded answer generation |
| M7 | 🐳 Production Deployment & Workers | Docker, PostgreSQL, Qdrant/PgVector, Redis, workers, monitoring, and deployment |

---


## 🚦 Current Development Focus

Current branch details are documented outside the README to keep this file stable.

### Current Branch

[`Branch 9 — Docker MongoDB Motor Infrastructure`](docs/milestones/milestone-04-database-document-models/branches/branch-09-docker-mongodb-motor.md)

Git branch:

```text
infra/9-docker-mongodb-motor
```

### Milestone Overview

[`Milestone 4 — Database & Document Models`](docs/milestones/milestone-04-database-document-models/milestone-04-database-document-models.md)

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
│   │   └── milestone-03-document-upload/
│   │       ├── milestone-03-document-upload.md
│   │       └── branches/
│   │           ├── branch-07-document-upload-endpoint.md
│   │           └── branch-08-document-processing-endpoint.md
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
Branch 7 → Document Upload Endpoint
Branch 8 → Document Processing Endpoint
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

---

## 👤 Author

**Dameur Mounir**

AI engineer and system builder focused on production-grade RAG, agentic AI systems, vector databases, observability, and deployable AI architectures.

My objective is to build practical, robust, and scalable AI systems that can evolve from learning projects into real products, client solutions, and future agentic platforms.
    