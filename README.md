# 🛠️ RAGForge

**RAGForge** is a production-oriented **Retrieval-Augmented Generation (RAG)** backend platform built step by step with real software engineering practices.

The project starts from a clean FastAPI backend and progressively evolves toward document ingestion, text extraction, chunking, embeddings, vector search, RAG answer generation, observability, background workers, deployment, and later agentic workflows.

RAGForge is not a notebook demo. It is designed as a long-term AI engineering project focused on building a clean, scalable, and professional backend architecture.

---

## 🎯 Project Vision

RAGForge aims to become a modular foundation for building production-ready RAG and agentic AI systems.

The project will evolve through structured milestones covering:

- ⚙️ FastAPI backend foundation
- 📄 document upload and processing
- 🗄️ metadata storage
- ✂️ text extraction and chunking
- 🧬 embedding generation
- 🔎 vector search
- 💬 RAG answer generation
- 📊 evaluation and observability
- ⏱️ background workers
- 🐳 Docker deployment
- 🧠 future LangGraph, MCP, and A2A integrations

The objective is to master the full engineering path from a basic backend service to a production-ready AI platform.

---

## 🚦 Current Status

```text
Milestone 3: File Upload & Document Processing
Current branch: feature/4-service-architecture-and-settings
Focus: Move backend to a professional src package architecture and prepare service-based structure
```

This branch starts Milestone 3 by restructuring the backend into a long-term architecture before adding the document upload endpoint.

Current focus:

- move FastAPI backend code into `src/ragforge/`
- introduce a production-oriented `src` layout
- prepare a service-oriented structure
- add `core/`, `services/`, `models/`, `schemas/`, `utils/`, and `exceptions/`
- move detailed documentation into `docs/`
- keep the main README short and strategic
- prepare the project for future document upload logic

---

## 🧱 Current Architecture

RAGForge now follows a **production-oriented FastAPI `src` architecture**.

```text
Route → Service → Storage / Database / Vector DB / LLM
```

The application code lives inside:

```text
src/ragforge/
```

Recommended structure:

```text
ragforge/
├── README.md
├── LICENSE
├── requirements.txt
├── .env.example
├── .gitignore
│
├── docs/
│   ├── milestones/
│   │   └── milestone-03-document-upload.md
│   ├── architecture/
│   │   └── backend-architecture.md
│   ├── setup/
│   │   └── local-development.md
│   └── api/
│       └── endpoints.md
│
├── resources/
│   └── ragforge.postman_collection.json
│
├── storage/
│   └── uploads/
│       └── .gitkeep
│
├── tests/
│   └── __init__.py
│
└── src/
    └── ragforge/
        ├── __init__.py
        ├── main.py
        ├── core/
        ├── routes/
        ├── services/
        ├── models/
        ├── schemas/
        ├── utils/
        └── exceptions/
```

---

## ✅ Implemented Features

### Milestone 1 — Project Bootstrap

- ✅ Repository initialized
- ✅ Python environment prepared
- ✅ Initial dependencies added
- ✅ GitHub workflow started
- ✅ Project vision documented

### Milestone 2 — FastAPI Backend Foundation

- ✅ FastAPI application created
- ✅ Uvicorn server configured
- ✅ Base route added
- ✅ Health check route added
- ✅ Environment variables supported with `.env`
- ✅ Swagger documentation available
- ✅ API version prefix added with `/api/v1`

### Milestone 3 — Current Branch

- ✅ Professional `src/ragforge/` architecture introduced
- ✅ Application code moved away from the repository root
- ✅ Documentation split into the `docs/` folder
- ✅ Runtime storage prepared with `storage/uploads/`
- ✅ Project prepared for future service-based document upload

---

## 🌐 Current API Endpoints

| Method | Endpoint | Status | Description |
|---|---|---|---|
| GET | `/api/v1/` | ✅ Implemented | Returns application metadata |
| GET | `/api/v1/health/` | ✅ Implemented | Returns API health status |
| POST | `/api/v1/documents/upload/{project_id}` | ⏳ Planned | Uploads a document for a project |
| GET | `/docs` | ✅ Implemented | Opens FastAPI Swagger UI |
| GET | `/redoc` | ✅ Implemented | Opens ReDoc documentation |

---

## 🚀 Quick Start

### 1. Activate environment

```bash
conda activate ragforge
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Prepare environment variables

```bash
cp .env.example .env
```

### 4. Run the API

Because the FastAPI app now lives inside `src/ragforge/main.py`, run:

```bash
uvicorn src.ragforge.main:app --reload --host 127.0.0.1 --port 8000
```

### 5. Open Swagger

```text
http://127.0.0.1:8000/docs
```

---

## 🧪 Test Current Endpoints

Base route:

```bash
curl http://127.0.0.1:8000/api/v1/
```

Health route:

```bash
curl http://127.0.0.1:8000/api/v1/health/
```

---

## ⚙️ Environment Variables

Example `.env.example`:

```env
APP_NAME=RAGForge
APP_VERSION=0.1.0
APP_ENV=development

FILE_ALLOWED_TYPES=application/pdf,text/plain,text/markdown
FILE_MAX_SIZE_MB=10
FILE_DEFAULT_CHUNK_SIZE=524288
```

The real `.env` file is private and must never be committed to GitHub.

---

## 📚 Documentation

The detailed documentation is now organized inside the `docs/` folder.

| Document | Purpose |
|---|---|
| [`docs/milestones/milestone-03-document-upload.md`](docs/milestones/milestone-03-document-upload.md) | Milestone 3 branch plan and document upload roadmap |
| [`docs/architecture/backend-architecture.md`](docs/architecture/backend-architecture.md) | Backend architecture, folder responsibilities, and design principles |
| [`docs/setup/local-development.md`](docs/setup/local-development.md) | Local setup, Conda, Uvicorn, testing, and common problems |
| [`docs/api/endpoints.md`](docs/api/endpoints.md) | Current and planned API endpoints |

The main README is intentionally short. Long explanations belong in `docs/`.

---

## 🗺️ Roadmap

| Milestone | Focus | Status |
|---|---|---|
| M1 | 🧱 Project Bootstrap & Environment | ✅ Completed |
| M2 | ⚙️ FastAPI Backend Foundation | ✅ Completed |
| M3 | 📄 File Upload & Document Processing | 🚧 In Progress |
| M4 | ✂️ Text Extraction & Chunking | ⏳ Planned |
| M5 | 🗄️ PostgreSQL Metadata Layer | ⏳ Planned |
| M6 | 🧬 Embeddings & Qdrant Vector Search | ⏳ Planned |
| M7 | 💬 RAG Answer Generation | ⏳ Planned |
| M8 | ⏱️ Background Jobs & Workers | ⏳ Planned |
| M9 | 🐳 Docker & Deployment | ⏳ Planned |
| M10 | 📊 Observability & Evaluation | ⏳ Planned |
| M11 | 🧠 LangGraph Agent Layer | ⏳ Planned |
| M12 | 🔌 MCP and A2A Integration | ⏳ Planned |

---

## 🌿 Development Workflow

RAGForge follows a professional GitHub workflow:

```text
Milestone → Issue → Branch → Pull Request → Merge
```

Current branch:

```text
feature/4-service-architecture-and-settings
```

Recommended commit for this branch:

```bash
git commit -m "refactor: move backend to src package architecture"
```

---

## 🧠 Engineering Principles

RAGForge follows these principles:

- keep routes thin
- move business logic to services
- keep runtime data outside source code
- keep project-level files at the repository root
- use environment-based configuration
- do not commit private `.env` files
- do not expose internal paths
- keep each branch focused on one responsibility
- document each milestone clearly

---

## 👤 Author

**Dameur Mounir**

AI engineer and system builder focused on production-grade RAG, agentic AI systems, vector databases, observability, and deployable AI architectures.

My objective is to build practical, robust, and scalable AI systems that can evolve from 
learning projects into real products, client solutions, and future agentic platforms.


