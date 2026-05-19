# Milestone 4 — Database & Document Models

## Objective

Milestone 4 introduces the first persistence layer for RAGForge.

After Milestone 3, RAGForge can upload documents, organize them by project, process supported files, extract text, and split content into chunks.

Milestone 4 moves the system from a file-only ingestion pipeline toward a database-backed ingestion system.

The goal is to add:

- MongoDB infrastructure
- async Motor database access
- project document structures
- document metadata models
- chunk models
- repository classes
- metadata persistence
- MongoDB indexes

At the end of this milestone, MongoDB should run locally, the API should connect to it, metadata should be persisted, and indexes should be created.

---

## Why This Milestone Matters

A production RAG backend cannot rely only on files and temporary API responses.

RAGForge needs a database layer to know:

- which projects exist
- which documents were uploaded
- where files are stored
- whether documents were processed
- how many chunks were generated
- which chunks belong to which document
- which chunks are ready for future embeddings
- which documents failed processing
- which fields need indexes for fast lookup

This milestone prepares RAGForge for the next production steps:

```text
document persistence
→ chunk persistence
→ indexed metadata
→ stable ingestion pipeline
→ embeddings
→ vector indexing
→ retrieval
→ grounded answer generation
```

---

## Architecture Direction

Milestone 4 follows the existing RAGForge backend architecture:

```text
Route
→ Schema
→ Service
→ Repository
→ Store / Database
→ Response
```

Folder responsibilities:

```text
core/              application configuration
docker/            infrastructure services
stores/            database clients and external storage clients
models/enums/      controlled application signals
models/db_schemes/ database document structures
schemas/           API request and response schemas
services/          business logic
repositories/      database persistence operations
routes/            HTTP endpoints
```

Database connection code belongs in:

```text
src/ragforge/stores/
```

Database document structures belong in:

```text
src/ragforge/models/db_schemes/
```

Database operations belong in:

```text
src/ragforge/repositories/
```

API request and response schemas remain in:

```text
src/ragforge/schemas/
```

---

## Architecture Evolution

Milestone 4 introduces:

```text
docker/
src/ragforge/stores/mongodb/
src/ragforge/models/db_schemes/
src/ragforge/repositories/
```

This keeps the MongoDB layer separate from API schemas and business services.

---

## Branch Plan

| Branch | Git Branch | Purpose | Status |
|---|---|---|---|
| Branch 9 | `infra/9-docker-mongodb-motor` | Add MongoDB Docker service, Motor dependency, MongoDB client, and FastAPI lifecycle connection | In Progress |
| Branch 10 | `feature/10-mongo-schemas-models` | Add MongoDB document schemes, repository/model classes, and metadata persistence | Planned |
| Branch 11 | `feature/11-mongo-indexing` | Add MongoDB indexes for projects, documents, chunks, and processing lookups | Planned |

---

## Branch 9 — Docker MongoDB Motor Infrastructure

### Goal

Add the first database infrastructure layer.

### Scope

- Add MongoDB service using Docker Compose
- Add MongoDB local data folder ignored by Git
- Add MongoDB environment variables
- Add Motor async dependency
- Add MongoDB client store
- Connect FastAPI lifecycle to MongoDB
- Preserve previous endpoints

### Out of Scope

- No document metadata persistence yet
- No chunk insertion yet
- No repository classes yet
- No MongoDB indexes yet

### Expected Result

RAGForge can start MongoDB locally and connect to it asynchronously from FastAPI.

---

## Branch 10 — MongoDB Schemas and Models

### Goal

Add the first MongoDB document structures and persistence classes.

### Planned Scope

- Add project database scheme
- Add document metadata database scheme
- Add chunk database scheme
- Add repository/model classes for MongoDB operations
- Create or retrieve a project by `project_id`
- Persist uploaded document metadata
- Persist processed chunks
- Link chunks to projects and documents
- Return inserted metadata and chunk counts

### Expected Collections

```text
projects
documents
chunks
```

### Expected Result

RAGForge should persist project metadata, document metadata, and processed chunks in MongoDB.

---

## Branch 11 — MongoDB Indexing

### Goal

Add database indexes to make project, document, and chunk lookups reliable and efficient.

### Planned Scope

- Add unique index on project identifier
- Add index on document ID
- Add index on project ID for documents
- Add index on file ID or stored filename if used
- Add compound index for chunks by document and chunk order
- Add index for chunks by project
- Add indexes needed for processing status queries
- Ensure indexes are created safely during application startup or repository initialization

### Example Index Targets

```text
projects.project_id
documents.document_id
documents.project_id
documents.processing_status
chunks.document_id + chunks.chunk_order
chunks.project_id
```

### Expected Result

MongoDB collections should have the indexes required for stable metadata and chunk retrieval.

---

## Expected Data Flow After Milestone 4

```text
Upload document
    ↓
Store file in project folder
    ↓
Create or load project metadata
    ↓
Create document metadata
    ↓
Process document
    ↓
Split text into chunks
    ↓
Store chunks in MongoDB
    ↓
Mark document as processed
    ↓
Use indexes for fast project/document/chunk lookup
```

---

## Current API Endpoints

Milestone 4 builds on the existing endpoints.

| Method | Endpoint | Status | Purpose |
|---|---|---|---|
| GET | `/api/v1/` | Implemented | Base API metadata |
| GET | `/api/v1/health/` | Implemented | Health check |
| POST | `/api/v1/documents/upload/{project_id}` | Implemented | Upload a document |
| POST | `/api/v1/documents/process/{project_id}` | Implemented | Process a stored document into chunks |

Branch 9 does not add a new public API endpoint.

Branches 10 and 11 may update existing upload and processing behavior to persist metadata, chunks, and indexes.

---

## Environment Variables

Milestone 4 introduces:

```env
MONGODB_URL=mongodb://localhost:27007
MONGODB_DATABASE=ragforge
```

These values are required for local development.

The local `.env` file must not be committed.

---

## Local Infrastructure

MongoDB runs through Docker Compose:

```bash
docker compose -f docker/docker-compose.yml up -d
```

MongoDB local port:

```text
27007
```

MongoDB container port:

```text
27017
```

MongoDB local data folder:

```text
docker/ragforge_mongodb_data/
```

This folder must remain ignored by Git.

---

## Storage and Persistence Direction

Milestone 4 separates storage responsibilities:

```text
Uploaded files
→ storage/uploads/{project_id}/documents/

MongoDB metadata
→ projects
→ documents
→ chunks
→ processing status
→ indexes
```

The file system keeps original uploaded files.

MongoDB keeps metadata and processed text structures.

Indexes make later lookup operations stable and efficient.

---

## Security and Repository Rules

The project must not commit:

- `.env`
- database credentials
- MongoDB runtime data
- uploaded user files
- internal absolute paths
- stack traces
- private local configuration

The repository should commit:

- Docker Compose configuration
- `.env.example`
- database client code
- database schemes
- repository classes
- index creation logic
- documentation

---

## Engineering Principles

Milestone 4 follows these principles:

- keep routes thin
- keep database client code outside routes
- keep database document schemes separate from API schemas
- keep database operations inside repositories
- keep runtime data out of Git
- use async database access
- centralize environment configuration
- create indexes explicitly
- keep each branch focused on one responsibility
- do not add embeddings before persistence and indexes are stable
- do not add vector search before chunk persistence is stable

---

## Milestone 4 Completion Criteria

Milestone 4 is complete when RAGForge can:

- start MongoDB locally with Docker Compose
- connect FastAPI to MongoDB using Motor
- expose a MongoDB database client to the application
- store project metadata
- store uploaded document metadata
- store processed chunks
- track processing status if required by the persistence flow
- create MongoDB indexes
- verify indexes in MongoDB
- keep all runtime data out of Git
- preserve the existing upload and processing API behavior
- prepare cleanly for the data pipeline checkpoint in Milestone 5

---

## Verification Commands

Start MongoDB:

```bash
docker compose -f docker/docker-compose.yml up -d
```

Open MongoDB shell:

```bash
docker exec -it ragforge-mongodb mongosh
```

Show database:

```javascript
use ragforge
show collections
```

After Branch 11, verify indexes:

```javascript
db.projects.getIndexes()
db.documents.getIndexes()
db.chunks.getIndexes()
```

---

## Final Result

At the end of Milestone 4, RAGForge should move from a file-based processing backend to a database-backed ingestion backend.

MongoDB should be running, FastAPI should connect to it, metadata should be persisted, and indexes should be created.

This prepares Milestone 5, where upload, storage, extraction, metadata, processing status, and reproducible workflows are connected into a stable data pipeline checkpoint.
