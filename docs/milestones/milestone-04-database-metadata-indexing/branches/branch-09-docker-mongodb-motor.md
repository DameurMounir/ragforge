# Branch 9 — Docker MongoDB Motor Infrastructure

## Branch Information

| Item | Value |
|---|---|
| Milestone | Milestone 4 — Database & Document Metadata |
| Branch number | Branch 9 |
| Git branch | `infra/9-docker-mongodb-motor` |
| Status | In Progress |

---

## Objective

This branch introduces the first database infrastructure layer for RAGForge.

It adds MongoDB as the metadata database and connects the FastAPI backend to MongoDB using the async Motor client.

The goal of this branch is not to persist uploaded documents or chunks yet.  
The goal is to prepare the backend so future branches can store:

- projects
- document metadata
- processing status
- extracted chunks
- future embedding metadata

---

## Why This Branch Matters

Milestone 3 completed the first document ingestion and processing flow:

```text
Upload document
→ Store document by project
→ Process stored document
→ Extract text
→ Split text into chunks
→ Return structured chunks
```

However, the system is still mostly file-based.

Branch 9 adds the missing database infrastructure foundation:

```text
FastAPI backend
→ Motor async client
→ MongoDB database
```

This prepares RAGForge for persistent metadata and chunk storage in the next branches.

---

## Architecture Decision

RAGForge keeps a clean separation of responsibilities:

```text
core/              application configuration
docker/            local infrastructure services
stores/            external storage and database clients
models/enums/      controlled application signals
models/db_schemes/ database document structures
schemas/           API request and response schemas
services/          business logic
routes/            HTTP endpoints
```

MongoDB connection logic belongs in:

```text
src/ragforge/stores/mongodb/
```

MongoDB document structures belong in:

```text
src/ragforge/models/db_schemes/
```

API schemas remain in:

```text
src/ragforge/schemas/
```

This avoids mixing API request validation with database document structure.

---

## Scope

This branch includes:

- Add Docker Compose infrastructure folder
- Add MongoDB service
- Expose MongoDB locally on port `27007`
- Store MongoDB local data in an ignored folder
- Add MongoDB environment variables
- Add Motor dependency
- Add MongoDB async client layer
- Connect FastAPI startup to MongoDB
- Connect FastAPI shutdown to MongoDB close logic
- Add initial MongoDB document schemes
- Preserve all existing endpoints from previous branches

---

## Out of Scope

This branch does not implement:

- document metadata persistence
- automatic project persistence during upload
- chunk insertion during processing
- processing status tracking
- MongoDB indexes
- search queries
- embeddings
- vector database integration
- Qdrant
- PGVector
- Celery workers
- LLM answer generation

Those responsibilities belong to later branches.

---

## Files Added

```text
docker/docker-compose.yml
docker/.gitignore

src/ragforge/stores/__init__.py
src/ragforge/stores/mongodb/__init__.py
src/ragforge/stores/mongodb/client.py

src/ragforge/models/db_schemes/__init__.py
src/ragforge/models/db_schemes/project.py
src/ragforge/models/db_schemes/data_chunk.py

docs/milestones/milestone-04-database-metadata/milestone-04-database-metadata.md
docs/milestones/milestone-04-database-metadata/branches/branch-09-docker-mongodb-motor.md
```

---

## Files Modified

```text
.env.example
requirements.txt
src/ragforge/core/config.py
src/ragforge/main.py
README.md
```

Optional documentation updates:

```text
docs/setup/local-development.md
docs/api/endpoints.md
```

No new public API endpoint is added in this branch.

---

## Docker Compose

MongoDB is managed with Docker Compose:

```text
docker/docker-compose.yml
```

Expected service:

```yaml
services:
  mongodb:
    image: mongo:7-jammy
    container_name: ragforge-mongodb
    restart: always

    ports:
      - '27007:27017'

    volumes:
      - ./ragforge_mongodb_data:/data/db

    networks:
      - backend

networks:
  backend:
```

MongoDB runs locally on:

```text
localhost:27007
```

The internal MongoDB container port remains:

```text
27017
```

MongoDB local data is stored in:

```text
docker/ragforge_mongodb_data/
```

---

## Docker Git Ignore Rule

Because the `.gitignore` file is inside the `docker/` folder, it should contain:

```gitignore
# MongoDB local Docker data
ragforge_mongodb_data/
```

This keeps local MongoDB runtime data out of Git.

---

## Environment Variables

The following variables are added to `.env.example`:

```env
MONGODB_URL=mongodb://localhost:27007
MONGODB_DATABASE=ragforge
```

The same values must exist in the local `.env` file.

The `.env` file must not be committed.

---

## Python Dependency

Motor is added as the async MongoDB driver:

```text
motor
```

Motor is used because RAGForge is built with FastAPI and should keep database communication asynchronous.

---

## Configuration Update

MongoDB settings are loaded through:

```text
src/ragforge/core/config.py
```

The `Settings` class includes:

```python
MONGODB_URL: str
MONGODB_DATABASE: str
```

This keeps MongoDB configuration centralized and consistent with the existing settings system.

---

## MongoDB Store Layer

The MongoDB connection is isolated in:

```text
src/ragforge/stores/mongodb/client.py
```

Responsibilities:

- create the async MongoDB client
- select the configured database
- verify the connection
- expose the database client to the application
- close the connection cleanly when the application shuts down

The FastAPI application stores the database reference for later usage:

```text
app.db_client
```

Future routes and services can use this database client without recreating a connection.

---

## FastAPI Lifecycle Integration

FastAPI connects to MongoDB when the backend starts.

FastAPI closes the MongoDB connection when the backend shuts down.

Expected lifecycle:

```text
Application startup
→ Load settings
→ Create MongoDB client
→ Select database
→ Attach database to app

Application shutdown
→ Close MongoDB connection
```

---

## Database Schemes

This branch adds initial MongoDB document schemes under:

```text
src/ragforge/models/db_schemes/
```

Initial schemes:

```text
Project
DataChunk
```

These are not API request schemas.  
They describe database document structures that future persistence logic can use.

---

## Project Scheme

The `Project` scheme represents a RAGForge project.

Expected fields:

```text
_id
project_id
```

The `project_id` field identifies the project namespace for uploaded documents and future stored chunks.

---

## DataChunk Scheme

The `DataChunk` scheme represents a processed text chunk.

Expected fields:

```text
_id
chunk_text
chunk_metadata
chunk_order
chunk_project_id
```

This prepares RAGForge to persist chunks generated by the document processing endpoint in future branches.

---

## Expected Local Commands

Start MongoDB:

```bash
docker compose -f docker/docker-compose.yml up -d
```

Check running containers:

```bash
docker ps
```

Open MongoDB shell:

```bash
docker exec -it ragforge-mongodb mongosh
```

Inside MongoDB:

```javascript
use ragforge
db.test.insertOne({ message: 'RAGForge MongoDB is working' })
db.test.find()
exit
```

Run FastAPI:

```bash
uvicorn src.ragforge.main:app --reload --host 127.0.0.1 --port 8000
```

Test existing endpoints:

```bash
curl http://127.0.0.1:8000/api/v1/
curl http://127.0.0.1:8000/api/v1/health/
```

---

## Verification Checklist

Branch 9 is complete when:

- MongoDB starts with Docker Compose
- MongoDB is reachable on `localhost:27007`
- MongoDB local data is stored in `docker/ragforge_mongodb_data/`
- MongoDB local data is ignored by Git
- `.env.example` contains MongoDB configuration
- local `.env` contains MongoDB configuration
- `.env` is not committed
- `motor` is installed
- `motor` is listed in `requirements.txt`
- `core/config.py` loads `MONGODB_URL`
- `core/config.py` loads `MONGODB_DATABASE`
- FastAPI starts without MongoDB connection errors
- FastAPI closes the MongoDB connection on shutdown
- `stores/mongodb/client.py` exists
- `models/db_schemes/project.py` exists
- `models/db_schemes/data_chunk.py` exists
- existing base endpoint still works
- existing health endpoint still works
- existing document upload endpoint still loads
- existing document processing endpoint still loads
- no MongoDB runtime data is committed
- no private `.env` file is committed

---

## Git Verification

Check ignored files:

```bash
git status --ignored
```

Expected ignored folder:

```text
docker/ragforge_mongodb_data/
```

Check tracked files:

```bash
git status
```

Expected files to commit:

```text
docker/docker-compose.yml
docker/.gitignore
.env.example
requirements.txt
src/ragforge/core/config.py
src/ragforge/main.py
src/ragforge/stores/
src/ragforge/models/db_schemes/
docs/milestones/milestone-04-database-metadata/
README.md
```

Do not commit:

```text
.env
docker/ragforge_mongodb_data/
storage/uploads/*
```

---

## Final Result

After this branch, RAGForge has its first database infrastructure layer.

The backend can now connect to MongoDB asynchronously and is ready for the next branches, where projects, document metadata, processing status, and chunks will be persisted.
