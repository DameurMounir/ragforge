# Milestone 4 — Database Metadata, Indexing & Ingestion Pipeline

## Goal

Milestone 4 builds the persistent metadata and ingestion foundation of RAGForge.

It connects:

```text
Project
  ↓
Asset
  ↓
Uploaded file
  ↓
Document processing
  ↓
DataChunk
  ↓
MongoDB persistence
```

The objective is to make RAGForge able to persist uploaded documents, track their metadata, process them into chunks, and preserve the relationship between every chunk and its source asset.

This milestone does not yet implement embeddings, vector search, semantic search, or answer generation. Those belong to Milestone 5.

## Architecture evolution

Before Milestone 4, RAGForge could upload and process documents mainly through local file logic.

After Milestone 4, RAGForge has a persistent metadata layer based on MongoDB:

```text
MongoDB
  ├── projects
  ├── assets
  └── data_chunks
```

And the backend can now persist:

```text
Project metadata
Asset metadata
Processing status
Chunk records
Project-to-asset relation
Asset-to-chunk relation
```

## Branches

| Branch | Name | Purpose |
|---|---|---|
| Branch 9 | Docker MongoDB Motor Infrastructure | Add MongoDB infrastructure using Docker and Motor. |
| Branch 10 | Asset Metadata Schemes & Stores | Add asset metadata models and stores. |
| Branch 11 | MongoDB Metadata Indexes & Auth | Add indexes and MongoDB authentication support. |
| Branch 12 | Upload and Processing Metadata Persistence | Persist upload metadata, processing metadata and chunk metadata. |
| Branch 13 | Data Pipeline Enhancements | Move processing orchestration into `PipelineService` and support processing one asset or all project assets. |

## Branch 9 — Docker MongoDB Motor Infrastructure

Branch 9 introduces the MongoDB infrastructure layer.

Main outcomes:

```text
Docker Compose
  ↓
MongoDB container
  ↓
Motor async client
  ↓
FastAPI database connection
```

This branch prepares RAGForge to move from local-only logic to persistent metadata storage.

## Branch 10 — Asset Metadata Schemes & Stores

Branch 10 introduces the metadata structures needed to describe uploaded files and future data sources.

Main outcomes:

```text
Project model
Asset model
DataChunk model
MongoDB stores
```

This branch makes the project able to represent the relationship:

```text
Project
  ↓
Asset
  ↓
DataChunk
```

## Branch 11 — MongoDB Metadata Indexes & Auth

Branch 11 strengthens the MongoDB layer.

Main outcomes:

```text
MongoDB authentication
Indexes
Reliable queries
Metadata lookup performance
```

This branch prepares the persistence layer for real ingestion and later retrieval workloads.

## Branch 12 — Upload and Processing Metadata Persistence

Branch 12 connects file upload and processing to MongoDB metadata.

Main outcomes:

```text
Upload endpoint
  ↓
Project metadata
  ↓
Asset metadata
  ↓
Processing metadata
  ↓
Chunk metadata
```

After this branch, uploaded files are no longer only physical files. They are represented as persisted assets.

## Branch 13 — Data Pipeline Enhancements

Branch 13 completes the ingestion pipeline by transforming the processing route into a clean orchestration flow.

Before Branch 13:

```text
documents.py handled processing logic directly
```

After Branch 13:

```text
documents.py
  ↓
PipelineService
  ↓
DocumentProcessingService
  ↓
Mongo stores
```

This keeps the route thin and makes the processing pipeline reusable for future workers, background jobs, and agentic layers.

## Branch 13 processing modes

The `/process/{project_id}` endpoint now supports three modes.

### 1. Process all project FILE assets

When no `asset_id` and no `stored_filename` are provided, all project `FILE` assets are processed.

```json
{
  "chunk_size": 500,
  "overlap_size": 50,
  "do_reset": true,
  "include_chunks": false
}
```

Mode:

```text
all_project_file_assets
```

### 2. Process one asset by asset_id

```json
{
  "asset_id": "MONGODB_ASSET_ID",
  "chunk_size": 500,
  "overlap_size": 50,
  "include_chunks": false
}
```

Mode:

```text
single_asset_by_id
```

### 3. Process one asset by stored_filename

```json
{
  "stored_filename": "stored_file_name.txt",
  "chunk_size": 500,
  "overlap_size": 50,
  "include_chunks": false
}
```

Mode:

```text
single_asset_by_filename
```

## Final Milestone 4 architecture

```text
FastAPI route
  ↓
Service orchestration
  ↓
MongoDB stores
  ↓
Persistent metadata
```

Detailed flow:

```text
Upload
  ↓
Project creation or lookup
  ↓
Asset creation
  ↓
File storage
  ↓
Processing request
  ↓
PipelineService
  ↓
DocumentProcessingService
  ↓
DataChunk creation
  ↓
ChunkStore persistence
  ↓
Asset status update
  ↓
Pipeline report
```

## Definition of done

Milestone 4 is complete when:

- MongoDB runs through Docker Compose.
- FastAPI connects to MongoDB.
- Projects are persisted.
- Uploaded files are persisted as assets.
- Asset metadata includes file name, stored name, size, type, storage path, and processing status.
- Documents can be processed into chunks.
- Chunks are persisted in MongoDB.
- Every chunk keeps `chunk_project_id`.
- Every chunk keeps `chunk_asset_id`.
- The processing endpoint can process one asset by `asset_id`.
- The processing endpoint can process one asset by `stored_filename`.
- The processing endpoint can process all project `FILE` assets.
- Asset processing status is updated after success or failure.
- The route remains thin.
- Pipeline orchestration lives in `PipelineService`.

## Final checkpoint

At the end of Milestone 4, RAGForge has a stable ingestion foundation:

```text
Upload
  ↓
Metadata persistence
  ↓
Document processing
  ↓
Chunk persistence
  ↓
Pipeline report
```

This prepares RAGForge for:

```text
Milestone 5 — RAG Core: LLM, Vector Store & Retrieval
```
