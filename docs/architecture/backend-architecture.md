# 🧱 RAGForge Backend Architecture

This document defines the **stable backend architecture** of RAGForge.

It is intentionally written as a long-term architecture reference for the whole project. It should **not be updated at every branch**. It should only change when the real system architecture changes in a major way, for example when adding a database layer, vector database layer, background worker layer, or deployment architecture.

---

## 🎯 Architecture Purpose

RAGForge is a production-oriented **Retrieval-Augmented Generation (RAG)** backend.

Its purpose is to provide a clean, modular, and scalable backend foundation for:

- document upload
- project-based storage
- file validation
- metadata management
- text extraction
- chunking
- embeddings
- vector search
- retrieval
- grounded answer generation
- background processing
- production deployment

RAGForge may later be used as a **tool or backend service inside agent systems**, but the core architecture of this project remains focused on building a strong RAG platform first.

---

## 🧠 Core Architecture Principle

The main architecture principle is:

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

Each layer has a clear responsibility.

Routes should remain thin.  
Services contain business logic.  
Infrastructure layers handle persistence, storage, vector search, model providers, and background execution.

---

## 🧩 High-Level RAGForge Architecture

```text
Client / API Consumer
        ↓
FastAPI API Layer
        ↓
Service Layer
        ↓
Document Storage
        ↓
Metadata Database
        ↓
Text Extraction
        ↓
Chunking Pipeline
        ↓
Embedding Service
        ↓
Vector Database
        ↓
Retrieval Service
        ↓
LLM Answer Generation
        ↓
Grounded API Response
```

This is the long-term direction of the project.

---

## 📦 Stable Project Structure

RAGForge follows a professional Python `src/` layout.

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
│   └── __init__.py
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
        │   ├── base_service.py
        │   ├── project_service.py
        │   ├── document_service.py
        │   ├── extraction_service.py
        │   ├── chunking_service.py
        │   ├── embedding_service.py
        │   ├── vector_store_service.py
        │   ├── retrieval_service.py
        │   └── rag_service.py
        │
        ├── models/
        │   ├── __init__.py
        │   └── enums/
        │       ├── __init__.py
        │       └── response_signals.py
        │
        ├── schemas/
        │   └── __init__.py
        │
        ├── repositories/
        │   └── __init__.py
        │
        ├── workers/
        │   └── __init__.py
        │
        ├── utils/
        │   └── __init__.py
        │
        └── exceptions/
            └── __init__.py
```

Not every file exists from the beginning. Some files appear progressively as milestones evolve.

This document describes the intended stable architecture, not only the current branch state.

---

# 1. Repository Root

The repository root contains project-level files.

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

These files are not part of the Python application package.

They are used for:

- documentation
- dependency management
- environment configuration
- runtime storage
- testing
- project resources

---

## Why `.env` stays at the root

`.env` is a runtime configuration file.

It belongs to the project environment, not inside the Python package.

Correct:

```text
.env
.env.example
```

Incorrect:

```text
src/ragforge/.env
```

The real `.env` file must never be committed to GitHub.

---

## Why `storage/` stays at the root

Uploaded files and runtime documents are data, not source code.

Correct:

```text
storage/uploads/
```

Incorrect:

```text
src/ragforge/uploads/
```

Keeping runtime data outside `src/` keeps the Python package clean.

---

# 2. Application Package

The real application code lives in:

```text
src/ragforge/
```

This makes RAGForge an importable Python package.

The package contains:

```text
main.py
core/
routes/
services/
models/
schemas/
repositories/
workers/
utils/
exceptions/
```

This structure supports clean growth from a small FastAPI backend into a full RAG backend.

---

# 3. FastAPI Application Entry Point

## File

```text
src/ragforge/main.py
```

Responsibilities:

- create the FastAPI app
- load application settings
- include routers
- define global app metadata
- prepare the API entry point

Example concept:

```python
from fastapi import FastAPI

from src.ragforge.core.config import get_settings
from src.ragforge.routes.base import base_router
from src.ragforge.routes.health import health_router
from src.ragforge.routes.documents import documents_router


settings = get_settings()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)


app.include_router(base_router)
app.include_router(health_router)
app.include_router(documents_router)
```

`main.py` should not contain business logic.

---

# 4. Routes Layer

## Folder

```text
src/ragforge/routes/
```

Routes define HTTP endpoints.

Their responsibility is to:

- receive HTTP requests
- read path parameters
- read query parameters
- read request bodies
- receive uploaded files
- call services
- return API responses

Routes should remain thin.

They should not contain heavy validation, storage logic, extraction logic, chunking logic, embedding logic, or retrieval logic.

---

## Route Examples

Current and future route groups may include:

```text
routes/base.py
routes/health.py
routes/documents.py
routes/projects.py
routes/search.py
routes/rag.py
routes/jobs.py
```

Example endpoint groups:

```text
GET  /api/v1/
GET  /api/v1/health/
POST /api/v1/documents/upload/{project_id}
POST /api/v1/projects/{project_id}/ask
GET  /api/v1/documents/{document_id}
GET  /api/v1/jobs/{job_id}
```

---

# 5. Services Layer

## Folder

```text
src/ragforge/services/
```

Services contain the business logic of the application.

This is the most important layer in RAGForge.

Services should be reusable by:

- FastAPI routes
- background workers
- tests
- command-line scripts
- future orchestration flows
- future agent systems that call RAGForge as a tool

---

## Core Service Types

### `BaseService`

Shared service foundation.

Responsibilities:

- load centralized settings
- expose common paths
- provide common helper methods
- avoid repeated low-level setup code

---

### `ProjectService`

Manages project-based storage and project path resolution.

Responsibilities:

- validate `project_id`
- prevent path traversal
- resolve upload directories
- create or reuse project folders
- keep project path logic outside routes

Target storage:

```text
storage/uploads/{project_id}/documents/
```

Important:

```text
ProjectService does not create a new project folder for every document.
It creates or reuses one folder per project.
```

---

### `DocumentService`

Handles upload-related document logic.

Responsibilities:

- validate uploaded file MIME type
- validate uploaded file size
- clean original filenames
- generate document IDs
- generate stored filenames
- prepare final storage paths
- coordinate with `ProjectService`

---

### `ExtractionService`

Future service responsible for extracting text.

Responsibilities:

- extract text from PDF
- extract text from TXT
- extract text from DOCX
- normalize extracted content
- prepare extracted content for chunking

---

### `ChunkingService`

Future service responsible for splitting text.

Responsibilities:

- split long documents into chunks
- preserve chunk order
- attach document metadata
- prepare chunks for embeddings

---

### `EmbeddingService`

Future service responsible for vector embeddings.

Responsibilities:

- connect to embedding provider
- generate embeddings for chunks
- generate embeddings for queries
- handle embedding configuration

---

### `VectorStoreService`

Future service responsible for vector database operations.

Responsibilities:

- create collections or indexes
- insert vectors
- search vectors
- delete vectors
- update payload metadata

Possible vector stores:

```text
Qdrant
PgVector
FAISS
```

---

### `RetrievalService`

Future service responsible for retrieving relevant context.

Responsibilities:

- receive user query
- generate query embedding
- search vector database
- filter by project or document
- return relevant chunks

---

### `RAGService`

Future service responsible for full RAG answer generation.

Responsibilities:

- receive user question
- call `RetrievalService`
- build grounded prompt
- call LLM provider
- return answer with sources

---

# 6. Core Layer

## Folder

```text
src/ragforge/core/
```

The `core/` folder contains core application configuration.

Main file:

```text
core/config.py
```

---

## `core/config.py`

This file centralizes configuration.

RAGForge should use Pydantic Settings instead of scattered `os.getenv()` calls.

Example:

```python
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = 'RAGForge'
    APP_VERSION: str = '0.1.0'
    APP_ENV: str = 'development'

    FILE_MAX_SIZE_MB: int = 20
    FILE_DEFAULT_CHUNK_SIZE: int = 1048576

    FILE_ALLOWED_EXTENSIONS: list[str] = ['pdf', 'txt', 'docx']
    FILE_ALLOWED_MIME_TYPES: list[str] = [
        'application/pdf',
        'text/plain',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]

    UPLOAD_DIR: str = 'storage/uploads'
    PROJECT_DOCUMENTS_DIR: str = 'documents'

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

Benefits:

- typed configuration
- default values
- validation
- centralized settings
- clean `.env` loading
- easier testing
- cleaner imports

---

# 7. Models Layer

## Folder

```text
src/ragforge/models/
```

The `models/` folder contains application-level models and enums.

Current example:

```text
models/
├── __init__.py
└── enums/
    ├── __init__.py
    └── response_signals.py
```

---

## Response Signals

Response signals make API responses stable and predictable.

Example:

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

Response signals help with:

- predictable API responses
- frontend integration
- testing
- refactoring
- clean API standards

---

# 8. Schemas Layer

## Folder

```text
src/ragforge/schemas/
```

Schemas define request and response structures using Pydantic.

Future examples:

```text
DocumentUploadResponse
DocumentMetadataResponse
DocumentListResponse
ProjectCreateRequest
ProjectResponse
RAGAnswerRequest
RAGAnswerResponse
SearchRequest
SearchResponse
JobStatusResponse
```

Schemas help:

- validate request bodies
- standardize responses
- improve OpenAPI documentation
- keep routes clean

---

# 9. Repositories Layer

## Folder

```text
src/ragforge/repositories/
```

This folder can be introduced when the database layer appears.

Repositories handle database access.

They should not contain business logic.

Responsibilities:

- create database records
- read database records
- update database records
- delete database records
- isolate SQL/database code from services

Example future files:

```text
project_repository.py
document_repository.py
chunk_repository.py
job_repository.py
```

Future flow:

```text
Service → Repository → Database
```

---

# 10. Database Layer

The database becomes the source of truth for structured metadata.

Future database responsibilities:

- store projects
- store documents
- store chunks
- store processing status
- store upload metadata
- store extraction status
- store embedding status
- store retrieval logs

Conceptual tables:

```text
projects
documents
chunks
processing_jobs
```

The filesystem stores raw files.

The database stores structured metadata.

---

# 11. Storage Layer

## Folder

```text
storage/
└── uploads/
    └── .gitkeep
```

The storage layer keeps uploaded runtime files.

Current target structure:

```text
storage/uploads/{project_id}/documents/{document_id}_{filename}
```

Future structure may become:

```text
storage/uploads/{project_id}/
├── documents/
├── extracted/
├── chunks/
└── metadata/
```

Important rules:

- storage is runtime data
- storage stays outside `src/`
- uploaded files are ignored by Git
- `.gitkeep` preserves the folder structure

Recommended `.gitignore` rule:

```gitignore
storage/uploads/*
!storage/uploads/.gitkeep
```

---

# 12. Vector Database Layer

The vector database stores embeddings for semantic search.

Possible vector database options:

```text
Qdrant
PgVector
FAISS
```

Vector database responsibilities:

- store chunk embeddings
- store vector payload metadata
- search by query embedding
- filter results by project, document, or metadata
- return relevant chunks

Conceptual flow:

```text
Chunk Text
    ↓
Generate Embedding
    ↓
Store Vector + Metadata
    ↓
Search by Query Embedding
    ↓
Return Relevant Chunks
```

---

# 13. Background Workers Layer

Background workers are used when processing becomes slow.

Possible worker tools:

```text
Celery
Redis
ARQ
RQ
```

Future responsibilities:

- extract text
- chunk documents
- generate embeddings
- index vectors
- update document status
- retry failed jobs
- run cleanup tasks

Future flow:

```text
Upload File
    ↓
Return document_id immediately
    ↓
Create processing job
    ↓
Worker extracts text
    ↓
Worker chunks text
    ↓
Worker generates embeddings
    ↓
Worker indexes vectors
    ↓
Document status becomes ready
```

---

# 14. RAG Pipeline

The central RAG pipeline is:

```text
Upload Document
    ↓
Store Original File
    ↓
Extract Text
    ↓
Clean Text
    ↓
Split Into Chunks
    ↓
Store Metadata
    ↓
Generate Embeddings
    ↓
Index in Vector Database
    ↓
Retrieve Relevant Chunks
    ↓
Generate Grounded Answer
```

This pipeline is the core of RAGForge.

---

# 15. RAG Answer Generation

Future answer endpoints may include:

```http
POST /api/v1/projects/{project_id}/ask
POST /api/v1/documents/{document_id}/summary
POST /api/v1/documents/{document_id}/quiz
```

Answer generation flow:

```text
User Question
    ↓
Embed Query
    ↓
Retrieve Relevant Chunks
    ↓
Build Prompt with Context
    ↓
Call LLM
    ↓
Return Grounded Answer + Sources
```

---

# 16. Relation to Agent Systems

RAGForge is focused first on RAG.

Later, an agent system can call RAGForge as a tool.

Example:

```text
Agent
  ↓ calls
RAGForge Search / Ask API
  ↓
RAGForge retrieves grounded context
  ↓
Agent uses returned knowledge
```

This means RAGForge can become a reliable knowledge backend for agents.

However, the current architecture does not depend on agent protocols or multi-agent communication.

The priority is to build a strong RAG backend first.

---

# 17. Security Principles

RAGForge should follow these security principles from the beginning.

## Do Not Trust

Do not blindly trust:

- uploaded filenames
- uploaded file extensions
- uploaded MIME types
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

# 18. Testing Layer

## Folder

```text
tests/
```

Tests live outside `src/`.

Future tests may include:

```text
test_base.py
test_health.py
test_document_upload.py
test_project_storage.py
test_file_validation.py
test_extraction.py
test_chunking.py
test_retrieval.py
```

Run tests with:

```bash
pytest -v
```

---

# 19. Documentation Strategy

RAGForge documentation should be split by responsibility.

```text
README.md
= short public landing page, current status, quick start, roadmap

docs/milestones/
= milestone progress, branch plans, implementation history

docs/api/
= endpoints, request examples, response examples

docs/setup/
= local setup, installation, running commands, common errors

docs/architecture/
= stable system architecture and design principles
```

This `backend-architecture.md` file should not be updated for every branch.

Update it only when the system architecture changes, for example:

- adding database/repository layer
- adding vector database layer
- adding background workers
- changing major folder responsibilities
- changing core architectural flow

---

# 20. Seven-Milestone Architecture Roadmap

RAGForge follows 7 major milestones:

```text
M1 — Project Bootstrap & Environment
M2 — FastAPI Backend Foundation
M3 — File Upload & Document Processing
M4 — Database & Document Models
M5 — Data Pipeline Checkpoint
M6 — RAG Core
M7 — Production Deployment & Workers
```

The architecture is designed so each milestone adds one stronger layer without breaking the previous layers.

---

# ✅ Summary

RAGForge uses:

```text
FastAPI src-layout
Service-based backend architecture
Project-based document storage
Centralized settings
Controlled response signals
Repository layer for future database access
Vector database layer for semantic search
Background workers for heavy processing
Runtime storage outside source code
```

This document is the long-term architecture reference for the project.

It should remain stable and should not be rewritten at every branch.
