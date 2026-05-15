# 🧱 Backend Architecture

This document explains the current backend architecture of **RAGForge** and the long-term structure that will support future RAG, vector search, background jobs, and agentic AI features.

RAGForge uses a **production-oriented FastAPI `src/` architecture** with a **service-based structure**.

---

## 🎯 Architecture Goal

The goal of the backend architecture is to keep the project:

- clean
- modular
- testable
- scalable
- easy to document
- ready for production
- ready for future AI engineering layers

RAGForge is not designed as a small script or notebook demo.

It is designed as a backend platform that can progressively evolve from a basic FastAPI API into a complete RAG and agentic AI system.

---

## 🧠 Core Architecture Principle

The main principle is:

```text
Route → Service → Storage / Database / Vector DB / LLM
```

Each layer has a clear responsibility.

```text
HTTP Request
    ↓
FastAPI Route
    ↓
Service Layer
    ↓
Storage / Database / Vector Store / LLM
    ↓
API Response
```

---

## 📦 Recommended Project Structure

```text
ragforge/
│
├── README.md
├── LICENSE
├── requirements.txt
├── .env.example
├── .env
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
│   ├── .gitkeep
│   └── ragforge.postman_collection.json
│
├── storage/
│   └── uploads/
│       └── .gitkeep
│
├── tests/
│   ├── __init__.py
│   ├── test_base.py
│   └── test_health.py
│
└── src/
    └── ragforge/
        ├── __init__.py
        ├── main.py
        │
        ├── core/
        │   ├── __init__.py
        │   └── config.py
        │
        ├── routes/
        │   ├── __init__.py
        │   ├── base.py
        │   ├── health.py
        │   └── documents.py
        │
        ├── services/
        │   ├── __init__.py
        │   ├── document_service.py
        │   └── project_service.py
        │
        ├── models/
        │   ├── __init__.py
        │   └── response_signals.py
        │
        ├── schemas/
        │   ├── __init__.py
        │   └── document_schema.py
        │
        ├── utils/
        │   ├── __init__.py
        │   └── file_utils.py
        │
        └── exceptions/
            ├── __init__.py
            └── document_exceptions.py
```

---

# 🧩 Why Use `src/ragforge/`?

The `src/ragforge/` folder contains the real Python application package.

This separates project-level files from application code.

```text
Repository root → project files
src/ragforge/   → Python application package
```

This is cleaner than placing all code directly in the project root.

---

## ✅ What Belongs in the Project Root?

The project root contains files and folders related to the whole repository:

```text
README.md
LICENSE
requirements.txt
.env.example
.env
.gitignore
docs/
resources/
storage/
tests/
```

These are not Python package modules.

They are project-level assets, configuration, documentation, runtime storage, and tests.

---

## ✅ What Belongs in `src/ragforge/`?

The `src/ragforge/` folder contains importable Python application code:

```text
main.py
core/
routes/
services/
models/
schemas/
utils/
exceptions/
```

This makes RAGForge a clean Python package.

---

# 🚀 Application Entry Point

## `src/ragforge/main.py`

This file creates the FastAPI application and includes the routers.

Example:

```python
from fastapi import FastAPI
from dotenv import load_dotenv

from src.ragforge.routes.base import base_router
from src.ragforge.routes.health import health_router


load_dotenv('.env')

app = FastAPI(
    title='RAGForge API',
    version='0.1.0',
    description='Production-oriented RAG and Agentic AI backend'
)

app.include_router(base_router)
app.include_router(health_router)
```

Later, when document upload is implemented:

```python
from src.ragforge.routes.documents import documents_router

app.include_router(documents_router)
```

---

# 🌐 Routes Layer

## Folder

```text
src/ragforge/routes/
```

Routes define HTTP endpoints.

Routes should stay thin.

They should only:

- receive requests
- read path/query/body parameters
- call services
- return responses

Routes should not contain heavy business logic.

---

## Current Routes

```text
routes/base.py
routes/health.py
```

Later:

```text
routes/documents.py
routes/search.py
routes/rag.py
routes/jobs.py
routes/projects.py
```

---

## Example Route Responsibility

A future document route should look like this conceptually:

```python
@documents_router.post('/upload/{project_id}')
async def upload_document(project_id: str, file: UploadFile):
    return await document_service.upload_document(project_id, file)
```

The route receives the request, then delegates logic to the service.

---

# ⚙️ Services Layer

## Folder

```text
src/ragforge/services/
```

Services contain business logic.

This is one of the most important folders in RAGForge.

Services will handle:

- document validation
- project storage
- file saving
- text extraction
- chunking
- embeddings
- vector indexing
- retrieval
- answer generation
- background job coordination

---

## Current Services

For Milestone 3, the planned services are:

```text
services/document_service.py
services/project_service.py
```

---

## Why Services Instead of Controllers?

Classical MVC uses controllers.

However, RAGForge is not a classical web application with HTML views.

RAGForge is an AI backend platform.

A cleaner architecture is:

```text
Route → Service → Infrastructure
```

Services can be reused later by:

- FastAPI routes
- Celery workers
- CLI scripts
- tests
- LangGraph agents

This is why `services/` is preferred over `controllers/`.

---

# 🧠 Core Layer

## Folder

```text
src/ragforge/core/
```

The `core/` folder contains global configuration and core application settings.

Main file:

```text
core/config.py
```

---

## Purpose of `core/config.py`

This file centralizes environment configuration.

Instead of using `os.getenv()` everywhere, RAGForge should use Pydantic Settings.

Example:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = 'RAGForge'
    APP_VERSION: str = '0.1.0'
    APP_ENV: str = 'development'

    FILE_ALLOWED_TYPES: str = 'application/pdf,text/plain,text/markdown'
    FILE_MAX_SIZE_MB: int = 10
    FILE_DEFAULT_CHUNK_SIZE: int = 524288

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )


settings = Settings()
```

Then any part of the app can use:

```python
from src.ragforge.core.config import settings

app_name = settings.APP_NAME
```

---

## Why Pydantic Settings?

Pydantic Settings provides:

- typed configuration
- default values
- validation
- clean `.env` loading
- centralized configuration
- easier testing
- cleaner imports

This is more professional than spreading `os.getenv()` across the codebase.

---

# 🧾 Models Layer

## Folder

```text
src/ragforge/models/
```

The `models/` folder contains application-level models, enums, and later database models.

For Milestone 3, it will contain:

```text
models/response_signals.py
```

---

## Response Signals

Response signals make API responses stable and predictable.

Example:

```python
from enum import Enum


class ResponseSignal(str, Enum):
    APP_HEALTHY = 'app_healthy'
    DOCUMENT_UPLOAD_SUCCESS = 'document_upload_success'
    DOCUMENT_UPLOAD_FAILED = 'document_upload_failed'
    DOCUMENT_TYPE_NOT_SUPPORTED = 'document_type_not_supported'
    DOCUMENT_SIZE_EXCEEDED = 'document_size_exceeded'
```

---

## Why Use Enums?

Enums prevent random response strings from spreading across the code.

Instead of this:

```python
return {'signal': 'upload ok'}
```

Use this:

```python
return {'signal': ResponseSignal.DOCUMENT_UPLOAD_SUCCESS}
```

Benefits:

- consistent responses
- easier testing
- easier frontend integration
- easier refactoring
- cleaner API documentation

---

# 📐 Schemas Layer

## Folder

```text
src/ragforge/schemas/
```

Schemas define request and response shapes using Pydantic.

For Milestone 3, a future file may be:

```text
schemas/document_schema.py
```

Possible future schemas:

```text
DocumentUploadResponse
DocumentMetadataResponse
DocumentListResponse
RAGAnswerRequest
RAGAnswerResponse
SearchRequest
SearchResponse
```

Schemas help FastAPI generate better OpenAPI documentation.

---

# 🛠️ Utils Layer

## Folder

```text
src/ragforge/utils/
```

The `utils/` folder contains small reusable helper functions.

Example:

```text
utils/file_utils.py
```

Possible utility functions:

- sanitize filenames
- extract file extensions
- generate safe names
- format file sizes
- normalize project IDs

Important rule:

```text
Small reusable helpers go in utils.
Business logic goes in services.
```

Do not put large application logic inside `utils/`.

---

# 🚨 Exceptions Layer

## Folder

```text
src/ragforge/exceptions/
```

The `exceptions/` folder contains custom exceptions.

Example:

```text
exceptions/document_exceptions.py
```

Possible future exceptions:

```text
UnsupportedFileTypeError
FileTooLargeError
DocumentUploadError
TextExtractionError
EmbeddingGenerationError
VectorStoreError
```

Custom exceptions make error handling cleaner and more explicit.

---

# 📁 Storage Layer

## Folder

```text
storage/
└── uploads/
    └── .gitkeep
```

The `storage/` folder is outside `src/` because it contains runtime data, not source code.

Uploaded files should be stored here during local development:

```text
storage/uploads/{project_id}/
```

Example:

```text
storage/uploads/default/
storage/uploads/client_demo/
storage/uploads/project_001/
```

---

## Why Not Put Uploads Inside `src/`?

Uploaded files are runtime data.

`src/` should contain only application code.

Correct:

```text
storage/uploads/
```

Incorrect:

```text
src/ragforge/uploads/
```

This separation keeps the codebase clean and avoids mixing source code with user data.

---

# 🧪 Tests

## Folder

```text
tests/
```

Tests live outside `src/`.

Current tests may include:

```text
tests/test_base.py
tests/test_health.py
```

Future tests:

```text
tests/test_document_upload.py
tests/test_project_storage.py
tests/test_file_validation.py
```

---

## Test Command

```bash
pytest -v
```

---

# 📚 Documentation

## Folder

```text
docs/
```

The `docs/` folder contains detailed project documentation.

Main sections:

```text
docs/milestones/
docs/architecture/
docs/setup/
docs/api/
```

The main README should stay short. Long explanations belong in `docs/`.

---

# 🔐 Environment Files

## `.env`

Private local environment file.

It should never be committed.

Example:

```env
APP_NAME=RAGForge
APP_VERSION=0.1.0
APP_ENV=development
```

---

## `.env.example`

Public environment template.

It should be committed to GitHub.

Example:

```env
APP_NAME=RAGForge
APP_VERSION=0.1.0
APP_ENV=development

FILE_ALLOWED_TYPES=application/pdf,text/plain,text/markdown
FILE_MAX_SIZE_MB=10
FILE_DEFAULT_CHUNK_SIZE=524288
```

---

## Why `.env` and `.env.example` Stay Outside `src/`

Environment files are project-level runtime configuration.

They are not Python application modules.

They belong at the repository root.

This makes setup easier:

```bash
cp .env.example .env
```

---

# 📦 Dependencies

## `requirements.txt`

The dependency file stays at the project root.

It is not application code.

Developers install dependencies using:

```bash
pip install -r requirements.txt
```

Docker and CI/CD will also expect dependency files at the project level.

---

# 🚀 Running the API

Because the app is inside `src/ragforge/main.py`, run:

```bash
uvicorn src.ragforge.main:app --reload --host 127.0.0.1 --port 8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 🧪 Testing Current Endpoints

Base route:

```bash
curl http://127.0.0.1:8000/api/v1/
```

Health route:

```bash
curl http://127.0.0.1:8000/api/v1/health/
```

---

# 🛡️ Security Principles

RAGForge should follow these backend security principles from the beginning:

## Do Not Trust

Do not blindly trust:

- uploaded filenames
- uploaded file extensions
- uploaded content types
- uploaded file sizes
- project IDs
- user input
- external data

## Do Not Expose

Do not expose:

- absolute server paths
- API keys
- `.env` values
- stack traces
- database credentials
- internal infrastructure details

---

# 🧭 Future Evolution

This architecture prepares RAGForge for:

```text
FastAPI
  ↓
Services
  ↓
PostgreSQL metadata
  ↓
Qdrant vector database
  ↓
Redis/Celery background workers
  ↓
RAG pipelines
  ↓
LangGraph agents
  ↓
MCP tools
  ↓
A2A agent communication
```

---

# ✅ Summary

RAGForge uses:

```text
Production-oriented FastAPI src-layout
Service-based backend architecture
Project-level documentation
Root-level configuration
Runtime storage outside source code
```

This structure is designed to live longer and support the growth of RAGForge from a simple FastAPI backend into a professional RAG and agentic AI platform.
