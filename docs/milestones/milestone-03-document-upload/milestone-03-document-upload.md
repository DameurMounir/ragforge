# 📄 Milestone 3 — File Upload & Document Processing

## 🎯 Objective

Milestone 3 introduces the first real **document ingestion foundation** in RAGForge.

The goal is to move from a basic FastAPI backend foundation to a backend that can:

- receive user documents
- validate uploaded files
- organize documents by project
- prepare files for future text extraction
- prepare the system for chunking, embeddings, vector search, and RAG generation

This milestone is intentionally divided into **small professional branches** instead of one large implementation branch.

---

## 🚀 Why This Milestone Matters

RAG systems start with documents.

Before adding embeddings, vector databases, retrieval, or LLM generation, the platform must first support a reliable document ingestion pipeline.

This milestone prepares the foundation for:

- 📥 document ingestion
- ✅ file validation
- 🗂️ project-based storage
- 📄 text extraction
- ✂️ chunking
- 🧾 metadata tracking
- ⏱️ background processing
- 🔎 vector indexing
- 💬 future RAG answer generation

The purpose is not only to make file upload work.  
The purpose is to build a clean backend structure that can later support production-grade RAG and agentic workflows.

---

## 🧱 Architecture Direction

RAGForge follows a service-oriented FastAPI architecture inspired by MVC principles.

```text
Route → Settings / Response Standards → Service → Storage / Database / Vector DB / LLM
```

Core principles:

- routes should stay thin
- configuration belongs in `core/`
- enums and constants belong in `models/`
- business logic belongs in `services/`
- runtime files belong in `storage/`
- documentation belongs in `docs/`
- API responses should be predictable and standardized
- user input must never be trusted blindly

---

## 🌿 Branch Plan

Milestone 3 is divided into four focused branches.

| Branch | Name | Purpose | Status |
|---|---|---|---|
| 1 | `feature/4-service-architecture-and-settings` | Prepare service architecture, Pydantic settings, docs structure, and clean README | ✅ Completed |
| 2 | `feature/5-response-signals-and-api-standards` | Add enums, response signals, file validation settings, and standard API conventions | ✅ Completed |
| 3 | `feature/6-project-storage-service` | Add dynamic project storage folders and safe storage structure | ⏳ Next |
| 4 | `feature/7-document-upload-endpoint` | Add upload endpoint, validation, safe filename, aiofiles, and chunked writing | ⏳ Planned |

---

# ✅ Branch 1 — Service Architecture and Settings

## Branch Name

```text
feature/4-service-architecture-and-settings
```

## Goal

Prepare the backend architecture before adding upload logic.

This branch does not implement the real upload endpoint yet.  
It creates the clean foundation needed for the next branches.

## Implemented

- Created a professional `src/ragforge/` package layout
- Moved backend code into the `src/` architecture
- Prepared core application structure
- Added `core/` for configuration
- Added `services/` for future business logic
- Added `models/` for future enums and constants
- Added `schemas/`, `utils/`, and `exceptions/`
- Added `docs/` structure
- Prepared `storage/uploads/`
- Updated README to become a short professional landing page

## Main Structure Added

```text
src/
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

## Recommended Commit

```bash
git add .
git commit -m "refactor: move backend to src package architecture"
git push -u origin feature/4-service-architecture-and-settings
```

---

# ✅ Branch 2 — Response Signals and API Standards

## Branch Name

```text
feature/5-response-signals-and-api-standards
```

## Goal

Introduce controlled API signals and standard response conventions.

This prepares RAGForge for predictable, maintainable API responses before implementing the real document upload endpoint.

## Implemented

- Added centralized response signals using Python Enum
- Organized enum files under `models/enums/`
- Updated the health endpoint to return a controlled response signal
- Updated base and health routes to use FastAPI dependency injection
- Added settings-based route responses using `Depends(get_settings)`
- Extended `core/config.py` with file validation configuration
- Updated `.env.example` with required app and upload-related settings
- Prepared API response conventions for future file validation and upload logic

---

## Response Signals Location

Response signals are stored in:

```text
src/ragforge/models/enums/response_signals.py
```

Current enum:

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

---

## Updated Health Response

The health endpoint now returns a standardized signal:

```json
{
  "signal": "app_healthy",
  "status": "healthy",
  "app_name": "RAGForge",
  "app_version": "0.1.0",
  "environment": "development",
  "timestamp": "2026-05-15T10:00:00+00:00"
}
```

Endpoint:

```text
GET /api/v1/health/
```

---

## Updated Base Response

The base route returns application metadata loaded from settings:

```json
{
  "message": "Hello and goodbye!",
  "app_name": "RAGForge",
  "app_version": "0.1.0",
  "environment": "development",
  "timestamp": "2026-05-15T10:00:00+00:00"
}
```

Endpoint:

```text
GET /api/v1/
```

---

## Settings Added

Application configuration is centralized in:

```text
src/ragforge/core/config.py
```

Current settings include:

```python
APP_NAME: str
APP_VERSION: str
APP_ENV: str

FILE_MAX_SIZE_MB: int
FILE_ALLOWED_EXTENSIONS: list[str]
FILE_ALLOWED_MIME_TYPES: list[str]
```

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

---

## Why This Branch Matters

This branch avoids duplicated raw strings in API responses.

Instead of returning uncontrolled values like:

```json
{
  "status": "ok"
}
```

RAGForge now uses controlled signals such as:

```text
app_healthy
file_validation_success
file_type_not_supported
file_size_exceeded
file_upload_success
file_upload_failed
internal_server_error
```

This makes API responses easier to:

- test
- document
- consume from frontend apps
- consume from workers
- consume from future agents
- maintain in production

## Recommended Commit

```bash
git add .
git commit -m "feat: add response signals and API standards"
git push -u origin feature/5-response-signals-and-api-standards
```

---

# ⏳ Branch 3 — Project Storage Service

## Branch Name

```text
feature/6-project-storage-service
```

## Goal

Create a safe storage layer for uploaded files.

Each project should have its own folder under:

```text
storage/uploads/
```

This prepares the future multi-project RAG architecture.

## What to Implement

- Create `services/project_service.py`
- Create or preserve `storage/uploads/.gitkeep`
- Update `.gitignore` to ignore real uploaded files but keep `.gitkeep`
- Create project folders dynamically using `pathlib`
- Validate or sanitize `project_id`
- Prevent path traversal attacks
- Do not expose absolute server paths in API responses

## Planned Storage Structure

```text
storage/
└── uploads/
    ├── .gitkeep
    ├── default/
    ├── project_001/
    └── client_demo/
```

## Recommended `.gitignore` Rule

```gitignore
storage/uploads/*
!storage/uploads/.gitkeep
```

## Planned Service Responsibility

`project_service.py` should be responsible for:

- resolving project upload paths
- creating missing project folders
- validating project identifiers
- returning safe internal `Path` objects to other services
- never returning absolute paths directly to API clients

## Recommended Commit

```bash
git add .
git commit -m "feat: add project storage service"
git push -u origin feature/6-project-storage-service
```

---

# ⏳ Branch 4 — Document Upload Endpoint

## Branch Name

```text
feature/7-document-upload-endpoint
```

## Goal

Add the real document upload endpoint using the architecture prepared in the previous branches.

This branch introduces the first real document ingestion capability of RAGForge.

## Endpoint

```http
POST /api/v1/documents/upload/{project_id}
```

## What to Implement

- Create `routes/documents.py`
- Create `services/document_service.py`
- Use `UploadFile` and `File` from FastAPI
- Validate uploaded file extension
- Validate uploaded file MIME type
- Validate uploaded file size
- Generate a UUID `document_id`
- Create a safe stored filename
- Save files with `aiofiles`
- Use chunked async writing
- Return controlled response signals
- Never expose absolute internal server paths

## Planned Successful Response

```json
{
  "signal": "file_upload_success",
  "message": "File uploaded successfully.",
  "document_id": "8f4d2f6e-2f64-4b3c-9e0c-31c25d52e021",
  "project_id": "default",
  "original_filename": "lesson.pdf",
  "stored_filename": "8f4d2f6e-2f64-4b3c-9e0c-31c25d52e021_lesson.pdf",
  "content_type": "application/pdf",
  "file_size": 245233,
  "uploaded_at": "2026-05-15T10:00:00+00:00"
}
```

## Planned Error Signals

| Signal | Meaning |
|---|---|
| `file_type_not_supported` | Uploaded extension or MIME type is not allowed |
| `file_size_exceeded` | Uploaded file exceeds max allowed size |
| `file_validation_failed` | Generic file validation failure |
| `file_upload_failed` | Upload failed unexpectedly |
| `internal_server_error` | Unexpected backend error |

## Recommended Commit

```bash
git add .
git commit -m "feat: add document upload endpoint"
git push -u origin feature/7-document-upload-endpoint
```

---

# 🌐 Current API Endpoints

| Method | Endpoint | Status | Description |
|---|---|---|---|
| GET | `/api/v1/` | ✅ Implemented | Returns basic application metadata |
| GET | `/api/v1/health/` | ✅ Implemented | Returns API health status with standardized signal |
| POST | `/api/v1/documents/upload/{project_id}` | ⏳ Planned | Uploads a document for a project |
| GET | `/docs` | ✅ Implemented | Opens FastAPI Swagger UI |
| GET | `/redoc` | ✅ Implemented | Opens ReDoc documentation |

---

# 🧪 Testing Current Branch

Run the API from the project root:

```bash
uvicorn src.ragforge.main:app --reload --host 127.0.0.1 --port 8000
```

Test base route:

```bash
curl http://127.0.0.1:8000/api/v1/
```

Test health route:

```bash
curl http://127.0.0.1:8000/api/v1/health/
```

Open Swagger:

```text
http://127.0.0.1:8000/docs
```

---

# 🛡️ Security Principles for Milestone 3

Uploaded files are untrusted input.

The API must not trust:

- uploaded filenames
- file extensions
- MIME types
- file sizes
- project IDs
- uploaded content

The API must not expose:

- absolute file paths
- server usernames
- internal directory structure
- `.env` values
- API keys
- stack traces
- database credentials

---

# 📚 Documentation Strategy

The README should remain a short professional landing page.

Detailed documentation should live inside:

```text
docs/
├── milestones/
│   └── milestone-03-document-upload.md
├── architecture/
│   └── backend-architecture.md
├── setup/
│   └── local-development.md
└── api/
    └── endpoints.md
```

Recommended documentation responsibilities:

| Document | Purpose |
|---|---|
| `README.md` | Short project landing page |
| `docs/milestones/milestone-03-document-upload.md` | This milestone plan |
| `docs/architecture/backend-architecture.md` | Backend architecture and folder responsibilities |
| `docs/setup/local-development.md` | Local setup and troubleshooting |
| `docs/api/endpoints.md` | Current and planned API endpoints |

---

# 🧠 Engineering Principles

Milestone 3 follows these engineering principles:

- keep routes thin
- move business logic to services
- centralize configuration in `core/config.py`
- organize enum values under `models/enums/`
- use controlled response signals
- avoid duplicated raw response strings
- use Pydantic settings instead of scattered `os.getenv`
- do not trust user input
- sanitize or validate `project_id`
- never expose internal paths
- use async chunked file writing for uploads
- keep each branch focused on one responsibility
- document every important architectural decision

---

# ✅ Current Milestone Progress

```text
Milestone 3 Progress

✅ Branch 1: Service Architecture and Settings
✅ Branch 2: Response Signals and API Standards
⏳ Branch 3: Project Storage Service
⏳ Branch 4: Document Upload Endpoint
```

This milestone moves RAGForge from a basic FastAPI app toward a professional backend foundation ready for document ingestion, file validation, storage, extraction, chunking, embeddings, Qdrant indexing, PostgreSQL metadata, background jobs, and future agentic layers.
