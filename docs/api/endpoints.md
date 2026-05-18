# 🌐 API Endpoints

This document describes the current and planned API endpoints for **RAGForge**.

RAGForge uses a versioned API structure:

```text
/api/v1
```

The goal is to keep the API clean, stable, predictable, and ready for future expansion.

---

## 🔗 Base URL

During local development:

```text
http://127.0.0.1:8000
```

API version prefix:

```text
/api/v1
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
| POST | `/api/v1/documents/upload/{project_id}` | ✅ Implemented | Uploads a document for a project |
| POST | `/api/v1/documents/process/{project_id}` | ✅ Implemented | Processes an uploaded document and returns text chunks |
| GET | `/docs` | ✅ Implemented | Opens FastAPI Swagger UI |
| GET | `/redoc` | ✅ Implemented | Opens ReDoc documentation |

---

# 🏠 GET `/api/v1/`

## Purpose

Returns basic metadata about the running RAGForge API.

This endpoint is useful for quickly checking that the API is running and that environment variables are loaded correctly.

---

## Request

```bash
curl http://127.0.0.1:8000/api/v1/
```

---

## Example Response

```json
{
  "message": "Hello and goodbye!",
  "app_name": "RAGForge",
  "app_version": "0.1.0",
  "environment": "development",
  "timestamp": "2026-05-15T10:00:00+00:00"
}
```

---

## Response Fields

| Field | Type | Description |
|---|---|---|
| `message` | string | Basic welcome message |
| `app_name` | string | Application name loaded from environment variables |
| `app_version` | string | Current application version |
| `environment` | string | Current runtime environment, such as `development` |
| `timestamp` | string | UTC timestamp of the response |

---

# 🩺 GET `/api/v1/health/`

## Purpose

Returns the health status of the API.

This endpoint is useful for:

- manual testing
- Docker health checks
- monitoring tools
- deployment readiness checks
- future CI/CD pipelines

---

## Request

```bash
curl http://127.0.0.1:8000/api/v1/health/
```

---

## Example Response

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

---

## Response Fields

| Field | Type | Description |
|---|---|---|
| `signal` | string | Stable API response signal |
| `status` | string | Current API health status |
| `app_name` | string | Application name |
| `app_version` | string | Current application version |
| `environment` | string | Current runtime environment |
| `timestamp` | string | UTC timestamp of the health check |

---

## Current Health Signal

The health endpoint currently uses:

```text
app_healthy
```

This signal is defined in:

```text
src/ragforge/models/enums/response_signals.py
```

---

## Future Health Checks

Later, this endpoint can be extended or split into more detailed checks:

| Endpoint | Purpose |
|---|---|
| `/api/v1/health/db` | Check PostgreSQL connection |
| `/api/v1/health/qdrant` | Check Qdrant vector database connection |
| `/api/v1/health/redis` | Check Redis connection |
| `/api/v1/health/workers` | Check background workers |
| `/api/v1/health/storage` | Check local or cloud storage availability |

---

# 📤 POST `/api/v1/documents/upload/{project_id}`

## Status

```text
Implemented in Branch 7 — Document Upload Endpoint
```

## Purpose

Uploads a document for a specific project.

This endpoint is the first real document ingestion endpoint in RAGForge.

The endpoint:

- receives a document
- validates the file MIME type
- validates the file size
- creates a project-specific upload folder
- generates a unique document ID
- generates a safe stored filename
- saves the file using async chunked writing
- returns clean upload metadata

---

## Endpoint

```http
POST /api/v1/documents/upload/{project_id}
```

---

## Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `project_id` | string | Yes | Project identifier used to organize uploaded documents |

Examples:

```text
default
project_001
project_003
client_demo
school_docs
```

---

## Request Type

This endpoint uses:

```text
multipart/form-data
```

Expected form field:

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | file | Yes | Uploaded document |

---

## File Validation Configuration

File validation rules are configured from environment variables and loaded through:

```text
src/ragforge/core/config.py
```

Current configuration keys:

```env
FILE_MAX_SIZE_MB=10
FILE_ALLOWED_EXTENSIONS=["pdf", "txt", "docx"]
FILE_ALLOWED_MIME_TYPES=["application/pdf", "text/plain", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
FILE_DEFAULT_CHUNK_SIZE=1048576
```

---

## Supported Upload Extensions

Initial supported upload extensions:

```text
pdf
txt
docx
```

Later, RAGForge may support:

```text
md
csv
json
html
pptx
xlsx
```

---

## Supported Upload MIME Types

Initial supported upload MIME types:

```text
application/pdf
text/plain
application/vnd.openxmlformats-officedocument.wordprocessingml.document
```

Later, RAGForge may support:

```text
text/markdown
text/csv
application/json
text/html
application/vnd.openxmlformats-officedocument.presentationml.presentation
application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
```

---

## Request Example with curl

Upload a text file:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/documents/upload/project_003" \
  -F "file=@intro_ragforg.txt"
```

Upload a PDF file:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/documents/upload/project_003" \
  -F "file=@/path/to/document.pdf"
```

---

## Successful Upload Response

```json
{
  "signal": "file_upload_success",
  "message": "Document uploaded successfully.",
  "document_id": "eaf4a826-821b-43c5-b544-5863abecff1a",
  "project_id": "project_003",
  "original_filename": "intro_ragforg.txt",
  "stored_filename": "eaf4a826-821b-43c5-b544-5863abecff1a_intro_ragforg.txt",
  "content_type": "text/plain",
  "file_size": 12403,
  "uploaded_at": "2026-05-15T10:00:00+00:00"
}
```

---

## Successful Upload Response Fields

| Field | Type | Description |
|---|---|---|
| `signal` | string | Stable API signal |
| `message` | string | Human-readable response message |
| `document_id` | string | Unique document identifier generated by the backend |
| `project_id` | string | Project where the file was uploaded |
| `original_filename` | string | Original filename received from the user |
| `stored_filename` | string | Safe filename generated by the backend |
| `content_type` | string | Uploaded file MIME type |
| `file_size` | integer | File size in bytes |
| `uploaded_at` | string | UTC upload timestamp |

---

# ⚙️ POST `/api/v1/documents/process/{project_id}`

## Status

```text
Implemented in Branch 8 — Document Processing Endpoint
```

## Purpose

Processes an uploaded document for a specific project.

The endpoint loads the stored document, extracts text content, splits the content into chunks, and returns a structured JSON response.

The endpoint:

- receives the `stored_filename` returned by the upload endpoint
- locates the document inside project storage
- detects the document extension
- loads supported document content
- splits extracted content into chunks
- returns chunk metadata and chunk content

---

## Endpoint

```http
POST /api/v1/documents/process/{project_id}
```

---

## Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `project_id` | string | Yes | Project identifier where the document is stored |

Example:

```text
project_003
```

---

## Request Type

This endpoint uses:

```text
application/json
```

---

## Request Body

```json
{
  "stored_filename": "eaf4a826-821b-43c5-b544-5863abecff1a_intro_ragforg.txt",
  "chunk_size": 1000,
  "overlap_size": 200,
  "do_reset": false
}
```

---

## Request Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `stored_filename` | string | Yes | Stored filename returned by the upload endpoint |
| `chunk_size` | integer | No | Maximum size of each text chunk |
| `overlap_size` | integer | No | Number of overlapping characters between chunks |
| `do_reset` | boolean | No | Reserved for future re-processing logic |

---

## Important Note About `stored_filename`

The processing endpoint uses `stored_filename`, not only `document_id`.

During upload, RAGForge stores documents using this format:

```text
storage/uploads/{project_id}/documents/{document_id}_{clean_filename}
```

Example:

```text
storage/uploads/project_003/documents/eaf4a826-821b-43c5-b544-5863abecff1a_intro_ragforg.txt
```

Because there is no database metadata layer yet, the safest current way to locate the file is to pass the complete `stored_filename` returned by the upload endpoint.

---

## Supported Processing Types

| Extension | Loader |
|---|---|
| `.txt` | `TextLoader` |
| `.pdf` | `PyMuPDFLoader` |

DOCX upload may be allowed by configuration, but DOCX processing is not included in this branch.

DOCX support can be added later with a dedicated loader.

---

## Request Example with curl

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/documents/process/project_003" \
  -H "Content-Type: application/json" \
  -d '{
    "stored_filename": "eaf4a826-821b-43c5-b544-5863abecff1a_intro_ragforg.txt",
    "chunk_size": 1000,
    "overlap_size": 200,
    "do_reset": false
  }'
```

---

## Successful Processing Response

```json
{
  "signal": "document_processing_success",
  "message": "Document processed successfully.",
  "project_id": "project_003",
  "stored_filename": "eaf4a826-821b-43c5-b544-5863abecff1a_intro_ragforg.txt",
  "chunk_size": 1000,
  "overlap_size": 200,
  "chunk_count": 20,
  "chunks": [
    {
      "chunk_index": 0,
      "content": "Extracted text chunk...",
      "metadata": {
        "source": "storage/uploads/project_003/documents/eaf4a826-821b-43c5-b544-5863abecff1a_intro_ragforg.txt"
      }
    }
  ]
}
```

---

## Successful Processing Response Fields

| Field | Type | Description |
|---|---|---|
| `signal` | string | Stable API signal |
| `message` | string | Human-readable response message |
| `project_id` | string | Project where the document is stored |
| `stored_filename` | string | Stored filename processed by the API |
| `chunk_size` | integer | Chunk size used during splitting |
| `overlap_size` | integer | Overlap size used during splitting |
| `chunk_count` | integer | Number of generated chunks |
| `chunks` | array | List of generated chunks |

---

## Chunk Object Fields

| Field | Type | Description |
|---|---|---|
| `chunk_index` | integer | Position of the chunk inside the processed document |
| `content` | string | Extracted text content for this chunk |
| `metadata` | object | Metadata returned by the document loader |

---

# ⚠️ Error Responses

## Unsupported File Type

Returned when the uploaded file MIME type is not allowed during upload.

### HTTP Status

```text
400 Bad Request
```

### Example Response

```json
{
  "signal": "file_type_not_supported",
  "message": "File validation failed."
}
```

---

## File Size Exceeded

Returned when the uploaded file exceeds the maximum allowed file size.

### HTTP Status

```text
400 Bad Request
```

### Example Response

```json
{
  "signal": "file_size_exceeded",
  "message": "File validation failed."
}
```

---

## File Validation Failed

Returned when file validation fails for a generic or unexpected validation reason.

### HTTP Status

```text
400 Bad Request
```

### Example Response

```json
{
  "signal": "file_validation_failed",
  "message": "File validation failed."
}
```

---

## Upload Failed

Returned when the upload process fails unexpectedly.

### HTTP Status

```text
500 Internal Server Error
```

### Example Response

```json
{
  "signal": "file_upload_failed",
  "message": "Document upload failed."
}
```

---

## Document Not Found

Returned when the requested `stored_filename` does not exist inside the project documents folder.

### HTTP Status

```text
404 Not Found
```

### Example Response

```json
{
  "signal": "document_not_found",
  "message": "Document not found."
}
```

---

## Document Type Not Supported for Processing

Returned when the file can be uploaded but cannot yet be processed by the current processing service.

### HTTP Status

```text
400 Bad Request
```

### Example Response

```json
{
  "signal": "document_type_not_supported",
  "message": "Document type not supported for processing"
}
```

---

## Empty Document Content

Returned when the document is found but no chunks are generated.

### HTTP Status

```text
400 Bad Request
```

### Example Response

```json
{
  "signal": "document_empty_content",
  "message": "Document content is empty."
}
```

---

## Document Processing Failed

Returned when an unexpected processing error occurs.

### HTTP Status

```text
500 Internal Server Error
```

### Example Response

```json
{
  "signal": "document_processing_failed",
  "message": "Document processing failed."
}
```

---

## Internal Server Error

Returned when an unexpected backend error occurs.

### HTTP Status

```text
500 Internal Server Error
```

### Example Response

```json
{
  "signal": "internal_server_error",
  "message": "Internal server error."
}
```

---

# 🧩 Response Signals

RAGForge uses stable response signals to make API responses predictable and easy to test.

Current signals:

```text
app_healthy
file_validation_success
file_validation_failed
file_type_not_supported
file_size_exceeded
file_upload_success
file_upload_failed
document_not_found
document_processing_success
document_processing_failed
document_type_not_supported
document_empty_content
internal_server_error
```

These signals are defined in:

```text
src/ragforge/models/enums/response_signals.py
```

Current enum structure:

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

    DOCUMENT_NOT_FOUND = 'document_not_found'
    DOCUMENT_PROCESSING_SUCCESS = 'document_processing_success'
    DOCUMENT_PROCESSING_FAILED = 'document_processing_failed'
    DOCUMENT_TYPE_NOT_SUPPORTED = 'document_type_not_supported'
    DOCUMENT_EMPTY_CONTENT = 'document_empty_content'

    INTERNAL_SERVER_ERROR = 'internal_server_error'
```

---

# 🛡️ Security Notes

Uploaded files are untrusted user input.

The API should not trust:

- uploaded filenames
- file extensions
- MIME types
- file sizes
- project IDs
- uploaded content
- processing request payloads

The API should not expose:

- absolute file paths
- server usernames
- internal directory structure
- `.env` values
- API keys
- stack traces
- database credentials

---

## Safe Metadata to Return

The API may safely return:

- document ID
- project ID
- original filename
- stored filename
- content type
- file size
- upload timestamp
- chunk count
- loader metadata when it does not expose sensitive internal data

---

## Unsafe Metadata to Avoid

Do not return absolute internal paths such as:

```text
/home/dameurmounir/development/tech/ai-engineering/projects/rag/ragforge/storage/uploads/default/file.pdf
```

Prefer:

```json
{
  "document_id": "8f4d2f6e-2f64-4b3c-9e0c-31c25d52e021",
  "stored_filename": "8f4d2f6e-2f64-4b3c-9e0c-31c25d52e021_lesson.pdf"
}
```

---

# 🧪 Testing with Swagger

Open:

```text
http://127.0.0.1:8000/docs
```

FastAPI automatically generates interactive documentation for all registered routes.

Current visible route groups:

```text
base
health
documents
```

The `documents` group should show:

```text
POST /api/v1/documents/upload/{project_id}
POST /api/v1/documents/process/{project_id}
```

---

# 🧪 Testing with curl

Base route:

```bash
curl http://127.0.0.1:8000/api/v1/
```

Health route:

```bash
curl http://127.0.0.1:8000/api/v1/health/
```

Upload route:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/documents/upload/project_003" \
  -F "file=@intro_ragforg.txt"
```

Process route:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/documents/process/project_003" \
  -H "Content-Type: application/json" \
  -d '{
    "stored_filename": "eaf4a826-821b-43c5-b544-5863abecff1a_intro_ragforg.txt",
    "chunk_size": 1000,
    "overlap_size": 200,
    "do_reset": false
  }'
```

---

# 🗺️ Future API Endpoints

Planned future endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/documents/{project_id}` | List uploaded documents for a project |
| GET | `/api/v1/documents/{project_id}/{document_id}` | Get document metadata |
| POST | `/api/v1/embeddings/{project_id}/{document_id}` | Generate embeddings |
| POST | `/api/v1/search/{project_id}` | Search similar chunks |
| POST | `/api/v1/rag/answer/{project_id}` | Generate RAG answer |
| GET | `/api/v1/jobs/{job_id}` | Get background job status |
| GET | `/api/v1/projects/` | List projects |
| POST | `/api/v1/projects/` | Create a project |

---

# 🧱 Current Architecture Link

The current API architecture follows:

```text
Route → Schema → Service → Storage / Database / Vector DB / LLM
```

For more details, see:

```text
docs/architecture/backend-architecture.md
```

---

# 📌 Notes

During Milestone 3, RAGForge now supports the first complete document ingestion flow:

```text
Upload document
→ Store document by project
→ Process uploaded document
→ Split text into chunks
→ Return structured chunks
```

Milestone 3 does not yet include:

- database persistence
- document metadata tables
- chunk tables
- embeddings
- Qdrant indexing
- answer generation

These features belong to later milestones.
