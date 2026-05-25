# Branch 13 — Data Pipeline Enhancements

Git branch:

```text
feature/13-data-pipeline-enhancements
```

Milestone:

```text
Milestone 4 — Database Metadata, Indexing & Ingestion Pipeline
```

## Goal

Improve the RAGForge document processing pipeline so that the `/process/{project_id}` endpoint can process:

1. one asset by `asset_id`,
2. one asset by `stored_filename`,
3. all `FILE` assets attached to a project when no specific asset is provided.

This branch transforms the processing endpoint from a single-file processor into a real ingestion pipeline endpoint.

## Why this branch exists

Branch 12 connected upload and processing to MongoDB metadata persistence.

Before Branch 13, the processing route was doing too much work directly:

```text
Route
  ↓
Project lookup
  ↓
Asset lookup
  ↓
DocumentProcessingService
  ↓
DataChunk creation
  ↓
Chunk deletion
  ↓
Chunk insertion
  ↓
Asset status update
  ↓
Response building
```

That made `documents.py` too heavy and too responsible for business orchestration.

Branch 13 moves the orchestration into `PipelineService`, so the route becomes thin and the architecture becomes cleaner.

## Architecture before Branch 13

```text
documents.py
  ├── receives request
  ├── finds project
  ├── finds asset
  ├── processes document
  ├── creates DataChunk objects
  ├── deletes old chunks
  ├── inserts new chunks
  ├── updates asset status
  └── returns response
```

Problem:

```text
The route had too many responsibilities.
```

## Architecture after Branch 13

```text
documents.py
  ↓
PipelineService
  ↓
DocumentProcessingService
  ↓
ChunkStore / AssetStore / ProjectStore
  ↓
MongoDB
```

Now responsibilities are separated:

```text
documents.py
  - receives HTTP request
  - creates stores
  - calls PipelineService
  - returns JSONResponse

PipelineService
  - resolves project
  - resolves one asset or all project assets
  - orchestrates processing
  - creates DataChunk objects
  - deletes old chunks correctly
  - inserts new chunks
  - updates asset status
  - returns a clean pipeline report

DocumentProcessingService
  - locates physical files
  - loads TXT/PDF documents
  - splits document content into chunks

Mongo stores
  - persist and retrieve Project, Asset and DataChunk records
```

## Main changes

- Make `stored_filename` optional in `ProcessDocumentRequest`.
- Add optional `asset_id`.
- Add `include_chunks`.
- Add `PipelineService`.
- Keep `/process/{project_id}` route thin.
- Support processing all project `FILE` assets.
- Support processing one asset by MongoDB `asset_id`.
- Support processing one asset by `stored_filename`.
- Use `Asset.storage_path` as the source of truth when processing files.
- Persist chunks with:
  - `chunk_project_id`
  - `chunk_asset_id`
  - `chunk_order`
  - `chunk_text`
  - `chunk_metadata`
- Update asset processing metadata after success or failure.
- Fix stored filename resolution using robust filename normalization.
- Return a clean pipeline report.

## New processing modes

### 1. Process all project files

Request:

```json
{
  "chunk_size": 500,
  "overlap_size": 50,
  "do_reset": true,
  "include_chunks": false
}
```

Expected mode:

```text
all_project_file_assets
```

### 2. Process one asset by asset_id

Request:

```json
{
  "asset_id": "MONGODB_ASSET_ID",
  "chunk_size": 500,
  "overlap_size": 50,
  "include_chunks": false
}
```

Expected mode:

```text
single_asset_by_id
```

### 3. Process one asset by stored_filename

Request:

```json
{
  "stored_filename": "stored_file_name.txt",
  "chunk_size": 500,
  "overlap_size": 50,
  "include_chunks": false
}
```

Expected mode:

```text
single_asset_by_filename
```

## API examples

### Process all files

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/documents/process/project13test" \
  -H "Content-Type: application/json" \
  -d '{"chunk_size":500,"overlap_size":50,"do_reset":true,"include_chunks":false}'
```

### Process one file by asset_id

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/documents/process/project13test" \
  -H "Content-Type: application/json" \
  -d '{"asset_id":"MONGODB_ASSET_ID","chunk_size":500,"overlap_size":50,"include_chunks":false}'
```

### Process one file by stored_filename

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/documents/process/project13test" \
  -H "Content-Type: application/json" \
  -d '{"stored_filename":"stored_file_name.txt","chunk_size":500,"overlap_size":50,"include_chunks":false}'
```

## Files changed

```text
src/ragforge/schemas/document_processing.py
src/ragforge/models/enums/response_signals.py
src/ragforge/services/document_processing_service.py
src/ragforge/services/pipeline_service.py
src/ragforge/routes/documents.py
docs/milestones/milestone-04-database-metadata-indexing/branches/branch-13-data-pipeline-enhancements.md
README.md
```

## Validation performed

Branch 13 was validated with three processing modes.

### Process all files

```text
mode = all_project_file_assets
signal = document_processing_success
processed_files > 0
failed_files = 0
```

### Process by asset_id

```text
mode = single_asset_by_id
signal = document_processing_success
processed_files = 1
failed_files = 0
```

### Process by stored_filename

```text
mode = single_asset_by_filename
signal = document_processing_success
processed_files = 1
failed_files = 0
```

## Definition of done

Branch 13 is complete when:

- Uploading multiple files to the same project works.
- Processing all project files works.
- Processing one file by `asset_id` works.
- Processing one file by `stored_filename` works.
- Old chunks are deleted correctly.
- New chunks are inserted correctly.
- Every chunk keeps its project and asset link.
- Asset status becomes `processed` after success.
- Asset status becomes `failed` after failure.
- The process route remains thin.
- Pipeline orchestration lives in `PipelineService`.

## Final result

Branch 13 completes the ingestion pipeline layer of Milestone 4.

RAGForge now has a clean foundation:

```text
Project
  ↓
Asset metadata
  ↓
Document processing
  ↓
Chunk persistence
  ↓
Pipeline report
```

This prepares the project for the next real milestone:

```text
Milestone 5 — RAG Core: LLM, Vector Store & Retrieval
```
