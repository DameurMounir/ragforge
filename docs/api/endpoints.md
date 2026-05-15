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
| POST | `/api/v1/documents/upload/{project_id}` | ⏳ Planned | Uploads a document for a project |
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
Planned for a later Milestone 3 branch
```

## Purpose

Uploads a document for a specific project.

This will be the first real document ingestion endpoint in RAGForge.

The endpoint will:

- receive a document
- validate the file extension
- validate the file MIME type
- validate the file size
- create a project-specific upload folder
- generate a safe stored filename
- save the file using async chunked writing
- return clean upload metadata

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
client_demo
school_docs
```

---

## Request Type

This endpoint will use:

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
```

---

## Supported File Extensions

Initial supported extensions:

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

## Supported MIME Types

Initial supported MIME types:

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
curl -X POST "http://127.0.0.1:8000/api/v1/documents/upload/default" \
  -F "file=@notes.txt"
```

Upload a PDF file:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/documents/upload/default" \
  -F "file=@/path/to/document.pdf"
```

---

## Planned Successful Upload Response

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

---

## Successful Response Fields

| Field | Type | Description |
|---|---|---|
| `signal` | string | Stable API signal |
| `message` | string | Human-readable response message |
| `document_id` | string | Unique document identifier |
| `project_id` | string | Project where the file was uploaded |
| `original_filename` | string | Original filename received from the user |
| `stored_filename` | string | Safe filename generated by the backend |
| `content_type` | string | Uploaded file MIME type |
| `file_size` | integer | File size in bytes |
| `uploaded_at` | string | UTC upload timestamp |

---

# ⚠️ Planned Error Responses

## Unsupported File Type

Returned when the uploaded file extension or MIME type is not allowed.

### Recommended HTTP Status

```text
400 Bad Request
```

### Example Response

```json
{
  "signal": "file_type_not_supported",
  "message": "Unsupported file type.",
  "allowed_extensions": [
    "pdf",
    "txt",
    "docx"
  ],
  "allowed_mime_types": [
    "application/pdf",
    "text/plain",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  ]
}
```

---

## File Size Exceeded

Returned when the uploaded file exceeds the maximum allowed file size.

### Recommended HTTP Status

```text
400 Bad Request
```

### Example Response

```json
{
  "signal": "file_size_exceeded",
  "message": "Uploaded file exceeds the maximum allowed size.",
  "max_size_mb": 10
}
```

---

## File Validation Failed

Returned when file validation fails for a generic or unexpected validation reason.

### Recommended HTTP Status

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

### Recommended HTTP Status

```text
500 Internal Server Error
```

### Example Response

```json
{
  "signal": "file_upload_failed",
  "message": "File upload failed."
}
```

---

## Internal Server Error

Returned when an unexpected backend error occurs.

### Recommended HTTP Status

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
Base
Health
```

After the document upload route is implemented, Swagger should also show:

```text
Documents
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

Future upload route:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/documents/upload/default" \
  -F "file=@README.md"
```

---

# 🗺️ Future API Endpoints

Planned future endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/documents/{project_id}` | List uploaded documents for a project |
| GET | `/api/v1/documents/{project_id}/{document_id}` | Get document metadata |
| POST | `/api/v1/documents/extract/{project_id}/{document_id}` | Extract text from a document |
| POST | `/api/v1/documents/chunk/{project_id}/{document_id}` | Split extracted text into chunks |
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
Route → Settings / Response Standards → Service → Storage / Database / Vector DB / LLM
```

For more details, see:

```text
docs/architecture/backend-architecture.md
```

---

# 📌 Notes

During Milestone 3, the upload endpoint will focus only on document reception and safe storage.

It will not yet perform:

- text extraction
- RAG chunking
- embeddings
- Qdrant indexing
- answer generation

Those features will come in later milestones.
