# 🌐 API Endpoints

This document describes the current API endpoints for **RAGForge** at the end of **Milestone 5 — Branch 18: Augmented Answers with Sources**.

RAGForge uses a versioned API structure:

```text
/api/v1
```

The goal is to keep the API clean, stable, predictable, source-aware, and ready for future production RAG and agentic-system expansion.

---

## 🔗 Base URL

During local development:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

ReDoc documentation:

```text
http://127.0.0.1:8000/redoc
```

---

## 📌 Current Endpoints

| Method | Endpoint | Status | Description |
|---|---|---|---|
| GET | `/api/v1/` | ✅ Implemented | Returns basic application metadata |
| GET | `/api/v1/health/` | ✅ Implemented | Returns API health status with a standardized response signal |
| POST | `/api/v1/documents/upload/{project_id}` | ✅ Implemented | Uploads a document for a project and persists project/asset metadata |
| POST | `/api/v1/documents/process/{project_id}` | ✅ Implemented | Processes one asset or all project FILE assets and persists chunks |
| POST | `/api/v1/llm/generate` | ✅ Implemented | Generates text through the provider-neutral LLM service |
| POST | `/api/v1/indexing/{project_id}` | ✅ Implemented | Embeds MongoDB chunks and indexes them into the vector database |
| POST | `/api/v1/search/{project_id}` | ✅ Implemented | Performs semantic search over indexed chunks and returns ranked evidence |
| POST | `/api/v1/answers/{project_id}` | ✅ Implemented | Generates grounded answers from retrieved evidence and returns sources |
| GET | `/docs` | ✅ Implemented | Opens FastAPI Swagger UI |
| GET | `/redoc` | ✅ Implemented | Opens ReDoc documentation |

---

# 🏠 GET `/api/v1/`

## Purpose

Returns basic metadata about the running RAGForge API.

## Request

```bash
curl http://127.0.0.1:8000/api/v1/
```

## Example Response

```json
{
  "message": "Hello and goodbye!",
  "app_name": "RAGForge",
  "app_version": "0.1.0",
  "environment": "development",
  "timestamp": "2026-06-04T19:50:00+00:00"
}
```

---

# 🩺 GET `/api/v1/health/`

## Purpose

Returns the health status of the API.

## Request

```bash
curl http://127.0.0.1:8000/api/v1/health/
```

## Example Response

```json
{
  "signal": "app_healthy",
  "status": "healthy",
  "app_name": "RAGForge",
  "app_version": "0.1.0",
  "environment": "development",
  "timestamp": "2026-06-04T19:50:00+00:00"
}
```

---

# 📤 POST `/api/v1/documents/upload/{project_id}`

## Status

```text
Implemented in Milestone 3 and connected to metadata persistence in Milestone 4
```

## Purpose

Uploads a document for a specific project.

The endpoint:

- receives a file,
- validates file extension, MIME type, and size,
- creates or reuses the project metadata record,
- creates a project-specific upload folder,
- generates a unique document ID,
- generates a safe stored filename,
- saves the file using async chunked writing,
- persists an Asset metadata record,
- returns clean upload metadata.

## Endpoint

```http
POST /api/v1/documents/upload/{project_id}
```

## Request Type

```text
multipart/form-data
```

Expected form field:

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | file | Yes | Uploaded document |

## Request Example

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/documents/upload/project18test"   -F "file=@tmp/branch18.txt"
```

## Successful Response Example

```json
{
  "signal": "file_upload_success",
  "message": "Document uploaded successfully.",
  "document_id": "4033d3f1-60b1-4d8e-a2ba-a965b1afb324",
  "asset_id": "6a21d720b5d8264b4c0feed9",
  "project_id": "project18test",
  "original_filename": "branch18.txt",
  "stored_filename": "4033d3f1-60b1-4d8e-a2ba-a965b1afb324_branch18.txt",
  "content_type": "text/plain",
  "file_size": 233,
  "uploaded_at": "2026-06-04T19:50:56.900195+00:00"
}
```

---

# ⚙️ POST `/api/v1/documents/process/{project_id}`

## Status

```text
Implemented in Milestone 3 and enhanced in Branch 13 — Data Pipeline Enhancements
```

## Purpose

Processes uploaded FILE assets for a project and persists extracted chunks into MongoDB.

The endpoint can process:

1. one asset by MongoDB `asset_id`,
2. one asset by `stored_filename`,
3. all FILE assets in the project when neither `asset_id` nor `stored_filename` is provided.

The endpoint:

- resolves the project,
- resolves one asset or all project FILE assets,
- loads supported document types,
- extracts text,
- splits text into chunks,
- persists new `DataChunk` records,
- updates asset processing status,
- returns a pipeline report.

## Endpoint

```http
POST /api/v1/documents/process/{project_id}
```

## Request Type

```text
application/json
```

## Request Body Examples

Process all project FILE assets:

```json
{
  "chunk_size": 500,
  "overlap_size": 50,
  "do_reset": true,
  "include_chunks": false
}
```

Process one asset by stored filename:

```json
{
  "stored_filename": "4033d3f1-60b1-4d8e-a2ba-a965b1afb324_branch18.txt",
  "chunk_size": 500,
  "overlap_size": 50,
  "include_chunks": false
}
```

Process one asset by asset id:

```json
{
  "asset_id": "6a21d720b5d8264b4c0feed9",
  "chunk_size": 500,
  "overlap_size": 50,
  "include_chunks": false
}
```

## Request Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `asset_id` | string or null | No | MongoDB asset id. Use this to process one asset by id. |
| `stored_filename` | string or null | No | Stored filename. Use this to process one asset by filename. |
| `chunk_size` | integer | No | Maximum size of each text chunk. |
| `overlap_size` | integer | No | Number of overlapping characters between chunks. Must be smaller than `chunk_size`. |
| `do_reset` | boolean | No | If true, deletes previous chunks according to selected processing mode. |
| `include_chunks` | boolean | No | If true, includes raw chunks in response. Defaults to false to avoid huge responses. |

## Request Example

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/documents/process/project18test"   -H "Content-Type: application/json"   -d '{"chunk_size":500,"overlap_size":50,"do_reset":true,"include_chunks":false}'
```

## Successful Response Example

```json
{
  "signal": "document_processing_success",
  "message": "Data pipeline processing completed.",
  "project_id": "project18test",
  "mode": "all_project_file_assets",
  "chunk_size": 500,
  "overlap_size": 50,
  "do_reset": true,
  "processed_files": 1,
  "failed_files": 0,
  "skipped_files": 0,
  "inserted_chunks": 1,
  "deleted_chunks": 0,
  "processed_assets": [
    {
      "asset_id": "6a21d720b5d8264b4c0feed9",
      "asset_name": "4033d3f1-60b1-4d8e-a2ba-a965b1afb324_branch18.txt",
      "file_name": "branch18.txt",
      "status": "processed",
      "inserted_chunks": 1
    }
  ],
  "failed_assets": [],
  "skipped_assets": []
}
```

## Processing Modes

| Mode | Trigger |
|---|---|
| `all_project_file_assets` | No `asset_id` and no `stored_filename` provided |
| `single_asset_by_id` | `asset_id` provided |
| `single_asset_by_filename` | `stored_filename` provided |

---

# 🤖 POST `/api/v1/llm/generate`

## Status

```text
Implemented in Branch 14 — LLM Factory
```

## Purpose

Generates text through the provider-neutral LLM layer.

This endpoint validates the LLM service independently from retrieval, indexing, and answer generation.

## Endpoint

```http
POST /api/v1/llm/generate
```

## Example Request

```json
{
  "provider": "fake",
  "prompt": "Explain what RAGForge is in one sentence.",
  "system_prompt": "You are a concise assistant.",
  "temperature": 0.2,
  "max_output_tokens": 512
}
```

## Example curl

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/llm/generate"   -H "Content-Type: application/json"   -d '{"provider":"fake","prompt":"Explain RAGForge in one sentence.","temperature":0.2,"max_output_tokens":512}'
```

---

# 🧬 POST `/api/v1/indexing/{project_id}`

## Status

```text
Implemented in Branch 16 — Embeddings & Indexing Foundation
```

## Purpose

Embeds stored MongoDB chunks and indexes them into the configured vector database collection.

The endpoint:

- resolves the project,
- optionally filters by `asset_id`,
- selects non-embedded or reset chunks,
- generates embeddings through the embedding provider layer,
- writes vectors through `VectorDBService`,
- updates chunk embedding metadata.

## Endpoint

```http
POST /api/v1/indexing/{project_id}
```

## Example Request

```json
{
  "asset_id": null,
  "do_reset": true,
  "batch_size": 2,
  "limit": 10,
  "strategy": "simple_chunk",
  "granularity": "chunk",
  "include_results": true
}
```

## Example curl

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/indexing/project18test"   -H "Content-Type: application/json"   -d '{"do_reset":true,"batch_size":2,"limit":10,"include_results":true}'
```

## Successful Response Example

```json
{
  "signal": "indexing_success",
  "message": "Indexing completed.",
  "project_id": "project18test",
  "asset_id": null,
  "strategy": "simple_chunk",
  "granularity": "chunk",
  "collection_name": "ragforge_chunks",
  "embedding_model": "fake-embedding-model",
  "indexed_chunks": 1,
  "failed_chunks": 0,
  "skipped_chunks": 0,
  "results": [
    {
      "chunk_id": "6a21d739b5d8264b4c0feeda",
      "asset_id": "6a21d720b5d8264b4c0feed9",
      "vector_id": "6a21d739b5d8264b4c0feeda",
      "chunk_order": 1,
      "embedding_model": "fake-embedding-model",
      "indexed": true
    }
  ]
}
```

---

# 🔍 POST `/api/v1/search/{project_id}`

## Status

```text
Implemented in Branch 17 — Semantic Search
```

## Purpose

Searches indexed project chunks by semantic similarity and returns ranked evidence.

The endpoint:

- receives a user query,
- generates a query embedding,
- searches the vector database through `VectorDBService`,
- normalizes source metadata,
- returns ranked evidence chunks.

## Endpoint

```http
POST /api/v1/search/{project_id}
```

## Example Request

```json
{
  "query": "What is RAGForge?",
  "limit": 5,
  "asset_id": null,
  "min_score": null,
  "include_text": true,
  "include_metadata": true
}
```

## Example curl

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/search/project18test"   -H "Content-Type: application/json"   -d '{"query":"What is RAGForge?","limit":5,"include_text":true,"include_metadata":true}'
```

## Successful Response Example

```json
{
  "signal": "semantic_search_success",
  "message": "Semantic search completed.",
  "project_id": "project18test",
  "query": "What is RAGForge?",
  "collection_name": "ragforge_chunks",
  "embedding_model": "fake-embedding-model",
  "total_results": 1,
  "results": [
    {
      "rank": 1,
      "score": 0.021401197,
      "record_id": "6a21d739b5d8264b4c0feeda",
      "chunk_id": "6a21d739b5d8264b4c0feeda",
      "asset_id": "6a21d720b5d8264b4c0feed9",
      "project_id": "6a21d720b5d8264b4c0feed8",
      "chunk_order": 1,
      "text": "RAGForge is a modular RAG backend...",
      "metadata": {
        "index_level": "chunk",
        "indexing_strategy": "simple_chunk",
        "source_type": "data_chunk",
        "embedding_model": "fake-embedding-model"
      }
    }
  ]
}
```

## Important Note About Fake Embeddings

The fake embedding provider uses deterministic pseudo-vectors. Scores validate the pipeline shape but should not be interpreted as real semantic quality scores. With real embedding providers, scores become semantically meaningful.

---

# 🧠 POST `/api/v1/answers/{project_id}`

## Status

```text
Implemented in Branch 18 — Augmented Answers with Sources
```

## Purpose

Generates a grounded answer from retrieved semantic evidence and returns structured sources.

This endpoint completes the first functional RAG Core loop:

```text
Question
  ↓
SemanticSearchService
  ↓
Ranked evidence chunks
  ↓
RAGContextBuilder
  ↓
RAG prompt builder
  ↓
LLMService
  ↓
Answer + Sources + Evidence
```

The endpoint:

- receives a user question,
- reuses Branch 17 semantic search,
- builds controlled source-numbered context,
- builds a grounded prompt,
- calls `LLMService`,
- returns answer, sources, evidence, model, and retrieval count,
- hides debug prompt by default.

## Endpoint

```http
POST /api/v1/answers/{project_id}
```

## Example Request

```json
{
  "question": "What is RAGForge?",
  "limit": 5,
  "asset_id": null,
  "min_score": null,
  "include_sources": true,
  "include_evidence": true,
  "include_debug_prompt": false
}
```

## Request Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `question` | string | Yes | User question to answer from retrieved evidence |
| `limit` | integer or null | No | Number of evidence chunks to retrieve. Defaults to config when null. |
| `asset_id` | string or null | No | Optional asset filter |
| `min_score` | float or null | No | Optional retrieval score threshold between 0 and 1 |
| `include_sources` | boolean or null | No | Whether to include structured source metadata |
| `include_evidence` | boolean or null | No | Whether to include retrieved evidence text |
| `include_debug_prompt` | boolean or null | No | Whether to return the generated prompt. Hidden by default. |

## Example curl

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/answers/project18test"   -H "Content-Type: application/json"   -d '{"question":"What is RAGForge?","limit":5,"include_sources":true,"include_evidence":true,"include_debug_prompt":false}'
```

## Successful Response Example

```json
{
  "signal": "rag_answer_success",
  "message": "Answer generated from retrieved evidence.",
  "project_id": "project18test",
  "question": "What is RAGForge?",
  "answer": "Fake RAGForge response generated successfully. Input preview: Question:
What is RAGForge?

Retrieved sources:
[Source 1] rank=1...",
  "sources": [
    {
      "source_number": 1,
      "rank": 1,
      "score": 0.021401197,
      "record_id": "6a21d739b5d8264b4c0feeda",
      "chunk_id": "6a21d739b5d8264b4c0feeda",
      "asset_id": "6a21d720b5d8264b4c0feed9",
      "project_id": "6a21d720b5d8264b4c0feed8",
      "chunk_order": 1,
      "metadata": {
        "index_level": "chunk",
        "indexing_strategy": "simple_chunk",
        "source_type": "data_chunk",
        "embedding_model": "fake-embedding-model"
      }
    }
  ],
  "evidence": [
    {
      "source_number": 1,
      "text": "RAGForge is a modular RAG backend. It uploads documents, processes them into chunks, stores metadata in MongoDB, indexes chunk embeddings into a vector database, performs semantic search, and generates grounded answers with sources.",
      "score": 0.021401197,
      "chunk_id": "6a21d739b5d8264b4c0feeda",
      "asset_id": "6a21d720b5d8264b4c0feed9",
      "chunk_order": 1,
      "metadata": {
        "index_level": "chunk",
        "indexing_strategy": "simple_chunk",
        "source_type": "data_chunk",
        "embedding_model": "fake-embedding-model"
      }
    }
  ],
  "llm_model": "fake-ragforge-model",
  "retrieval_count": 1,
  "debug_prompt": null
}
```

## No Context Response Example

```json
{
  "signal": "rag_answer_no_context",
  "message": "No relevant indexed evidence was found.",
  "project_id": "project18test",
  "question": "Unknown question?",
  "answer": "I cannot generate a grounded answer because no relevant indexed evidence was found for this project.",
  "sources": [],
  "evidence": [],
  "llm_model": null,
  "retrieval_count": 0,
  "debug_prompt": null
}
```

## Design Notes

The answer endpoint stays provider-neutral:

- it does not call the vector database directly,
- it does not call the embedding provider directly,
- it does not call concrete LLM providers directly,
- it reuses `SemanticSearchService`,
- it calls `LLMService`,
- it keeps prompt construction isolated.

---

# 🧪 End-to-End Branch 18 Validation Flow

Use this flow to validate the full RAG Core path locally.

## 1. Start infrastructure

```bash
sudo service docker start

docker compose --env-file .env -f docker/docker-compose.yml up -d
```

## 2. Start FastAPI

```bash
uvicorn src.ragforge.main:app --reload --host 127.0.0.1 --port 8000
```

## 3. Create a test file

```bash
mkdir -p tmp

cat > tmp/branch18.txt << 'EOF'
RAGForge is a modular RAG backend. It uploads documents, processes them into chunks, stores metadata in MongoDB, indexes chunk embeddings into a vector database, performs semantic search, and generates grounded answers with sources.
EOF
```

## 4. Upload

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/documents/upload/project18test"   -F "file=@tmp/branch18.txt"
```

## 5. Process

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/documents/process/project18test"   -H "Content-Type: application/json"   -d '{"chunk_size":500,"overlap_size":50,"do_reset":true,"include_chunks":false}'
```

## 6. Index

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/indexing/project18test"   -H "Content-Type: application/json"   -d '{"do_reset":true,"batch_size":2,"limit":10,"include_results":true}'
```

## 7. Search

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/search/project18test"   -H "Content-Type: application/json"   -d '{"query":"What is RAGForge?","limit":5,"include_text":true,"include_metadata":true}'
```

## 8. Answer

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/answers/project18test"   -H "Content-Type: application/json"   -d '{"question":"What is RAGForge?","limit":5,"include_sources":true,"include_evidence":true,"include_debug_prompt":false}'
```

## 9. Run validation script

```bash
python scripts/validation/validate_branch_18_answers.py
```

Expected:

```text
Branch 18 answer validation passed
```

---

# ⚠️ Error Responses

## Common Error Signals

| Signal | Typical HTTP Status | Meaning |
|---|---:|---|
| `project_not_found` | 404 | Requested project does not exist in MongoDB |
| `asset_not_found` | 404 / 400 | Requested asset does not exist or asset id is invalid |
| `no_files_to_process` | 400 | Project has no FILE assets to process |
| `file_validation_failed` | 400 | Generic file validation failure |
| `file_type_not_supported` | 400 | Uploaded MIME type or extension is not allowed |
| `file_size_exceeded` | 400 | Uploaded file exceeds configured max size |
| `file_upload_failed` | 500 | Unexpected upload failure |
| `document_not_found` | 404 | Physical document or metadata was not found |
| `document_processing_success` | 200 | Document processing completed successfully |
| `document_processing_partial_success` | 200 | Some assets processed, some failed |
| `document_processing_failed` | 500 / 400 | Processing failed |
| `document_type_not_supported` | 400 | File cannot be processed by current loaders |
| `document_empty_content` | 400 | Extracted document content is empty |
| `indexing_success` | 200 | Indexing completed successfully |
| `indexing_failed` | 500 / 400 | Indexing failed |
| `semantic_search_success` | 200 | Semantic search completed successfully |
| `semantic_search_no_results` | 200 | Search completed but no evidence matched |
| `semantic_search_failed` | 500 / 400 | Search failed |
| `rag_answer_success` | 200 | Grounded answer generated successfully |
| `rag_answer_no_context` | 200 | No usable evidence was found for grounded answering |
| `rag_answer_failed` | 500 / 404 / 400 | Answer generation failed during retrieval or LLM generation |
| `internal_server_error` | 500 | Unexpected backend error |

---

# 🧩 Response Signals

RAGForge uses stable response signals to make API responses predictable and easy to test.

Current important signals include:

```text
app_healthy
internal_server_error
project_not_found
asset_not_found
no_files_to_process
file_validation_success
file_validation_failed
file_type_not_supported
file_size_exceeded
file_upload_success
file_upload_failed
document_not_found
document_processing_success
document_processing_partial_success
document_processing_failed
document_type_not_supported
document_empty_content
indexing_success
indexing_failed
semantic_search_success
semantic_search_no_results
semantic_search_failed
rag_answer_success
rag_answer_no_context
rag_answer_failed
```

These signals are defined in:

```text
src/ragforge/models/enums/response_signals.py
```

---

# 🛡️ Security Notes

Uploaded files and request payloads are untrusted user input.

The API should not trust:

- uploaded filenames,
- file extensions,
- MIME types,
- file sizes,
- project IDs,
- uploaded content,
- processing request payloads,
- search queries,
- answer questions,
- prompt-related input.

The API should not expose:

- absolute file paths,
- server usernames,
- internal directory structure,
- `.env` values,
- API keys,
- stack traces,
- database credentials,
- debug prompts unless explicitly requested and safe.

## Safe Metadata to Return

The API may safely return:

- project id,
- document id,
- asset id,
- chunk id,
- original filename,
- stored filename,
- content type,
- file size,
- upload timestamp,
- chunk count,
- source metadata when it does not expose sensitive internal details.

## Debug Prompt Safety

Branch 18 includes `include_debug_prompt`, but the default must remain:

```text
false
```

Debug prompts are useful during local validation but should not be exposed casually in production.

---

# 🧪 Testing with Swagger

Open:

```text
http://127.0.0.1:8000/docs
```

FastAPI automatically generates interactive documentation for all registered routes.

Current visible route groups should include:

```text
base
health
documents
llm
indexing
search
answers
```

Important current endpoints:

```text
GET  /api/v1/
GET  /api/v1/health/
POST /api/v1/documents/upload/{project_id}
POST /api/v1/documents/process/{project_id}
POST /api/v1/llm/generate
POST /api/v1/indexing/{project_id}
POST /api/v1/search/{project_id}
POST /api/v1/answers/{project_id}
```

---

# 🗺️ Future API Endpoints

Planned future endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/projects/` | List projects |
| POST | `/api/v1/projects/` | Create a project explicitly |
| GET | `/api/v1/documents/{project_id}` | List uploaded documents/assets for a project |
| GET | `/api/v1/documents/{project_id}/{asset_id}` | Get document/asset metadata |
| GET | `/api/v1/chunks/{project_id}` | List stored chunks for a project |
| GET | `/api/v1/jobs/{job_id}` | Get background job status |
| POST | `/api/v1/evaluations/rag` | Evaluate RAG answer quality |
| POST | `/api/v1/admin/reindex/{project_id}` | Admin-triggered reindexing flow |

Removed from future list because they are now implemented:

```text
POST /api/v1/search/{project_id}
POST /api/v1/answers/{project_id}
```

---

# 🧱 Current Architecture Link

The current API architecture follows:

```text
Route → Schema → Service → Store / Provider Interface → Provider Implementation
```

Branch 18 answer architecture:

```text
Answers Route
  ↓
RAGAnswerService
  ↓
SemanticSearchService
  ↓
RAGContextBuilder
  ↓
RAG Prompt Builder
  ↓
LLMService
  ↓
Answer + Sources + Evidence
```

For more details, see:

```text
docs/architecture/backend-architecture.md
```

---

# 📌 Notes

At the end of Branch 18, RAGForge supports the first full RAG Core v1 flow:

```text
Upload document
→ Persist project and asset metadata
→ Process uploaded document
→ Persist chunks
→ Generate embeddings
→ Index vectors
→ Search semantic evidence
→ Build source-numbered context
→ Generate grounded answer
→ Return answer with sources and evidence
```

Branch 18 does not include:

- agents,
- chat memory,
- hybrid search,
- reranking,
- streaming responses,
- background workers,
- observability dashboards,
- production deployment.

These belong to later branches and milestones.
