# 🛠️ RAGForge

**RAGForge** is a production-oriented **Retrieval-Augmented Generation (RAG)** backend platform built step by step with real software engineering practices.

The project starts from a clean FastAPI backend and progressively evolves toward document ingestion, file validation, project-based storage, text extraction, chunking, embeddings, vector search, RAG answer generation, observability, background workers, deployment, and later agentic workflows.

RAGForge is not a notebook demo. It is designed as a long-term AI engineering project focused on building a clean, scalable, and professional backend architecture.

---

## 🎯 Project Vision

RAGForge aims to become a modular foundation for building production-ready RAG and agentic AI systems.

The project will evolve through structured milestones covering:

- ⚙️ FastAPI backend foundation
- 📄 document upload and processing
- 📡 standardized API responses
- 🗂️ project-based file storage
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
Current branch: feature/6-project-based-file-storage
Focus: Add project-based file storage service and safe upload directory foundation
```

This branch completes the third part of Milestone 3 by introducing the local storage foundation required before implementing the real document upload endpoint.

Current focus:

- create a reusable base service for shared service utilities
- create a project service responsible for project-based storage folders
- prepare the `storage/uploads/` runtime directory
- keep uploaded files out of Git while preserving the folder structure
- centralize storage settings in `core/config.py`
- expose storage configuration through `.env.example`
- prepare the backend for future document upload, validation, and async file writing
- keep routes thin by moving storage logic into services

---

## 🧱 Current Architecture

RAGForge follows a **production-oriented FastAPI `src` architecture**.

```text
Route → Service → Storage / Database / Vector DB / LLM
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
        │   ├── __init__.py
        │   ├── base_service.py
        │   └── project_service.py
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

### Milestone 3 — Branch 3: Project-Based File Storage

- ✅ `BaseService` added as a shared foundation for service classes
- ✅ `ProjectService` added to manage project-based storage folders
- ✅ Storage settings added to `core/config.py`
- ✅ `.env.example` updated with storage-related variables
- ✅ `storage/uploads/.gitkeep` added to preserve runtime upload structure
- ✅ `.gitignore` updated to ignore real uploaded files
- ✅ Project storage prepared using the structure:

```text
storage/
└── uploads/
    └── {project_id}/
        └── documents/
```

This branch does not implement the real document upload endpoint yet. It only prepares the storage layer that the next branch will use.

---

## 🗂️ Project-Based Storage

RAGForge now prepares project-based storage for future uploaded documents.

Target structure:

```text
storage/
└── uploads/
    └── project_001/
        └── documents/
            └── uploaded files
```

The storage layer is handled by:

```text
src/ragforge/services/base_service.py
src/ragforge/services/project_service.py
```

### Service responsibilities

`BaseService`:

- loads centralized settings
- exposes shared storage paths
- provides common directory utilities

`ProjectService`:

- validates project identifiers
- resolves project upload paths
- creates project document folders
- keeps path logic outside API routes

This keeps the architecture clean:

```text
Route → Service → Storage
```

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

RAGForge uses centralized response signals to make API responses predictable and easier to consume by frontend clients, workers, services, and future agentic layers.

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

## ⚙️ Settings and Configuration

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
- upload storage directory
- project document folder name

Example `.env.example`:

```env
APP_NAME="RAGForge"
APP_VERSION="0.1.0"
APP_ENV="development"

FILE_MAX_SIZE_MB=10
FILE_ALLOWED_EXTENSIONS=["pdf", "txt", "docx"]
FILE_ALLOWED_MIME_TYPES=["application/pdf", "text/plain", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]

UPLOAD_DIR="storage/uploads"
PROJECT_DOCUMENTS_DIR="documents"

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
| M3.3 | 🗂️ Project-Based File Storage | ✅ Completed |
| M3.4 | 📄 Document Upload Endpoint | ⏳ Next |
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
feature/6-project-based-file-storage
```

Recommended commit for this branch:

```bash
git commit -m "feat: add project-based file storage service"
```

Next branch:

```text
feature/7-document-upload-endpoint
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
- isolate project-based storage logic inside services
- keep runtime data outside source code
- keep uploaded files out of Git
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
