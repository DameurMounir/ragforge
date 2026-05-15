# 🛠️ RAGForge

**RAGForge** is a production-oriented **Retrieval-Augmented Generation (RAG)** backend platform built step by step with real software engineering practices.

The project starts from a clean FastAPI backend and progressively evolves toward document ingestion, file validation, storage services, text extraction, chunking, embeddings, vector search, RAG answer generation, observability, background workers, deployment, and later agentic workflows.

RAGForge is not a notebook demo. It is designed as a long-term AI engineering project focused on building a clean, scalable, and professional backend architecture.

---

## 🎯 Project Vision

RAGForge aims to become a modular foundation for building production-ready RAG and agentic AI systems.

The project will evolve through structured milestones covering:

- ⚙️ FastAPI backend foundation
- 📄 document upload and processing
- 📡 standardized API responses
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
Current branch: feature/5-response-signals-and-api-standards
Focus: Add response signals, API standards, settings injection, and file validation configuration
```

This branch completes the second part of Milestone 3 by introducing a centralized response signal system and cleaner API response conventions before implementing the real document upload endpoint.

Current focus:

- create centralized response signals using Python Enum
- organize enum-related code inside `models/enums/`
- standardize the health endpoint response with a controlled signal
- use FastAPI dependency injection with `Depends(get_settings)`
- extend application settings for future file validation
- prepare upload-related environment variables
- keep routes thin and predictable
- prepare the backend for future upload validation, storage, and document processing logic

---

## 🧱 Current Architecture

RAGForge follows a **production-oriented FastAPI `src` architecture**.

```text
Route → Settings / Response Standards → Service → Storage / Database / Vector DB / LLM
```

The application code lives inside:

```text
src/ragforge/
```

Current structure:

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
        │   ├── __init__.py
        │   └── config.py
        ├── routes/
        │   ├── __init__.py
        │   ├── base.py
        │   └── health.py
        ├── services/
        ├── models/
        │   ├── __init__.py
        │   └── enums/
        │       ├── __init__.py
        │       └── response_signals.py
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

### Milestone 3 — Branch 1: Service Architecture and Settings

- ✅ Professional `src/ragforge/` architecture introduced
- ✅ Application code moved away from the repository root
- ✅ Documentation split into the `docs/` folder
- ✅ Runtime storage prepared with `storage/uploads/`
- ✅ Project prepared for future service-based document upload

### Milestone 3 — Branch 2: Response Signals and API Standards

- ✅ Centralized API response signals added with Python Enum
- ✅ Enum files organized under `src/ragforge/models/enums/`
- ✅ Health endpoint updated with a controlled response signal
- ✅ Base and health routes updated to use FastAPI dependency injection
- ✅ Application settings loaded through `core/config.py`
- ✅ Upload-related configuration prepared:
  - `FILE_MAX_SIZE_MB`
  - `FILE_ALLOWED_EXTENSIONS`
  - `FILE_ALLOWED_MIME_TYPES`
- ✅ `.env.example` updated with required application and file settings
- ✅ API response structure prepared for future upload validation and storage logic

---

## 🌐 Current API Endpoints

| Method | Endpoint | Status | Description |
|---|---|---|---|
| GET | `/api/v1/` | ✅ Implemented | Returns application metadata |
| GET | `/api/v1/health/` | ✅ Implemented | Returns API health status with a standardized signal |
| POST | `/api/v1/documents/upload/{project_id}` | ⏳ Planned | Uploads a document for a project |
| GET | `/docs` | ✅ Implemented | Opens FastAPI Swagger UI |
| GET | `/redoc` | ✅ Implemented | Opens ReDoc documentation |

---

## 📡 Response Signals

RAGForge now uses centralized response signals to make API responses predictable and easier to consume by frontend clients, workers, services, and future agentic layers.

Response signals are stored in:

```text
src/ragforge/models/enums/response_signals.py
```

Current response signal enum:

```python
from enum import Enum


class ResponseSignal(str, Enum):
    APP_HEALTHY = 'app_healthy'

    FILE_VALIDATION_SUCCESS = 'file_validation_success'
    FILE_VALIDATION_FAILED = 'file_validation_failed'
    FILE_TYPE_NOT_SUPPORTED = 'file_type_not_supported'
    FILE_SIZE_EXCEEDED = 'file_size_exceeded'

    FILE_UPLOAD_SUCCESS = 'file_upload_success'
    FILE_UPLOAD_FAILED = 'file_upload_failed'

    INTERNAL_SERVER_ERROR = 'internal_server_error'
```

Example health response:

```json
{
  "signal": "app_healthy",
  "status": "healthy",
  "app_name": "RAGForge",
  "app_version": "0.1.0",
  "environment": "development",
  "timestamp": "2026-05-15T20:00:00+00:00"
}
```

---

## ⚙️ Settings and File Configuration

Application configuration is centralized in:

```text
src/ragforge/core/config.py
```

The settings layer currently supports:

- application name
- application version
- application environment
- maximum accepted file size
- allowed file extensions
- allowed MIME types

Example `.env.example`:

```env
APP_NAME="RAGForge"
APP_VERSION="0.1.0"
APP_ENV="development"

FILE_MAX_SIZE_MB=10
FILE_ALLOWED_EXTENSIONS=["pdf", "txt", "docx"]
FILE_ALLOWED_MIME_TYPES=["application/pdf", "text/plain", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]

OPENAI_API_KEY=""
```

The real `.env` file is private and must never be committed to GitHub.

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

Because the FastAPI app lives inside `src/ragforge/main.py`, run:

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

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Expected health response:

```json
{
  "signal": "app_healthy",
  "status": "healthy",
  "app_name": "RAGForge",
  "app_version": "0.1.0",
  "environment": "development",
  "timestamp": "..."
}
```

---

## 📚 Documentation

The detailed documentation is organized inside the `docs/` folder.

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
| M3.1 | 🧱 Service Architecture and Settings | ✅ Completed |
| M3.2 | 📡 Response Signals and API Standards | ✅ Completed |
| M3.3 | 🗂️ Project Storage Service | ⏳ Next |
| M3.4 | 📄 Document Upload Endpoint | ⏳ Planned |
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
feature/5-response-signals-and-api-standards
```

Recommended commit for this branch:

```bash
git commit -m "feat: add response signals and API standards"
```

Next branch:

```text
feature/6-project-storage-service
```

---

## 🧠 Engineering Principles

RAGForge follows these principles:

- keep routes thin
- move business logic to services
- centralize configuration in `core/config.py`
- use FastAPI dependency injection where appropriate
- organize enum values under `models/enums/`
- use controlled response signals instead of duplicated raw strings
- prepare validation rules before implementing upload logic
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

My objective is to build practical, robust, and scalable AI systems that can evolve from learning projects into real products, client solutions, and future agentic platforms.
