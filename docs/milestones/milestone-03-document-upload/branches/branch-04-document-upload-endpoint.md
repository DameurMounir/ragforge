# 🌿 Branch 4 — Document Upload Endpoint

## Branch Name

```text
feature/7-document-upload-endpoint
```

---

## 🎯 Goal

Add the first real document upload endpoint to RAGForge.

This branch completes the upload foundation of **Milestone 3 — File Upload & Document Processing** by connecting the API layer to the service layer and the project-based storage layer.

The objective is not only to upload a file, but to implement the upload flow in a clean backend architecture:

```text
Route → DocumentService → ProjectService → storage/uploads/{project_id}/documents/
```

---

## 🧠 Why This Branch Matters

Before this branch, RAGForge had:

- a clean FastAPI structure
- centralized settings
- response signals
- a service layer foundation
- project-based storage folders

This branch adds the first real ingestion capability:

```text
Client / Postman / WordPress
        ↓
Upload document
        ↓
RAGForge validates and stores the file
        ↓
Document becomes ready for future processing
```

This is the first concrete step toward the future RAG pipeline:

```text
Upload → Extract → Chunk → Embed → Index → Retrieve → Generate Answer
```

---

## 🧱 Architecture Flow

```text
Client / Postman / WordPress
        ↓
POST /api/v1/documents/upload/{project_id}
        ↓
src/ragforge/routes/documents.py
        ↓
DocumentService
        ↓
ProjectService
        ↓
storage/uploads/{project_id}/documents/
```

### Layer Responsibilities

| Layer | Responsibility |
|---|---|
| `documents.py` route | Receives HTTP request, file, and `project_id` |
| `DocumentService` | Validates file, cleans filename, generates document ID and stored filename |
| `ProjectService` | Validates project ID and creates/reuses project folder |
| `storage/uploads/` | Stores uploaded runtime files outside source code |

---

## ✅ Main Changes

This branch adds:

- `DocumentService`
- `documents_router`
- `POST /api/v1/documents/upload/{project_id}`
- file MIME type validation
- file size validation
- safe filename cleaning
- UUID-based `document_id` generation
- stored filename generation
- async chunked file writing with `aiofiles`
- project-based file saving
- controlled API responses using `ResponseSignal`
- upload testing with Postman

---

## 📁 Files Created

```text
src/ragforge/services/document_service.py
src/ragforge/routes/documents.py
```

---

## 📁 Files Updated

```text
src/ragforge/main.py
src/ragforge/core/config.py
src/ragforge/services/project_service.py
src/ragforge/routes/__init__.py
requirements.txt
.env.example
docs/api/endpoints.md
README.md
```

Note: `.env` may be updated locally, but it must **not** be committed.

---

## 📄 Endpoint Added

```http
POST /api/v1/documents/upload/{project_id}
```

Example:

```http
POST http://127.0.0.1:8000/api/v1/documents/upload/project_1
```

---

## 📤 Postman Request

Use:

```text
Body → form-data
```

| Key | Type | Value |
|---|---|---|
| `file` | File | any allowed PDF, TXT, or DOCX file |

Important:

```text
The form-data key must be exactly: file
```

Because the FastAPI route receives:

```python
file: UploadFile = File(...)
```

---

## 🧪 Upload Flow

```text
1. Client sends a file and a project_id.
2. FastAPI route receives the request.
3. DocumentService validates the file MIME type.
4. DocumentService validates the file size.
5. DocumentService cleans the original filename.
6. DocumentService generates a UUID document_id.
7. ProjectService validates the project_id.
8. ProjectService creates or reuses:
   storage/uploads/{project_id}/documents/
9. The route writes the file by chunks using aiofiles.
10. The API returns a clean JSON response.
```

---

## 📦 Storage Result

Uploaded files are stored under:

```text
storage/uploads/{project_id}/documents/
```

Example:

```text
storage/uploads/project_1/documents/
```

Stored filename format:

```text
{document_id}_{clean_filename}
```

Example:

```text
storage/uploads/project_1/documents/550e8400-e29b-41d4-a716-446655440000_lesson.pdf
```

Important:

```text
ProjectService does not create a new project folder for every document.
It creates or reuses one folder per project.
```

---

## ✅ Success Response Example

```json
{
  "signal": "file_upload_success",
  "message": "Document uploaded successfully.",
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "project_id": "project_1",
  "original_filename": "lesson.pdf",
  "stored_filename": "550e8400-e29b-41d4-a716-446655440000_lesson.pdf",
  "content_type": "application/pdf",
  "file_size": 245233,
  "uploaded_at": "2026-05-18T10:00:00+00:00"
}
```

---

## ⚠️ Validation Response Examples

### File size exceeded

```json
{
  "signal": "file_size_exceeded",
  "message": "File validation failed."
}
```

### Unsupported file type

```json
{
  "signal": "file_type_not_supported",
  "message": "File validation failed."
}
```

### Invalid project ID

```json
{
  "signal": "file_validation_failed",
  "message": "Invalid project_id"
}
```

---

## ⚙️ Settings Used

The upload endpoint depends on settings from:

```text
src/ragforge/core/config.py
```

Required settings:

```python
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
```

---

## 🧾 Environment Variables

The public `.env.example` should contain:

```env
FILE_MAX_SIZE_MB=20
FILE_DEFAULT_CHUNK_SIZE=1048576
FILE_ALLOWED_EXTENSIONS=["pdf", "txt", "docx"]
FILE_ALLOWED_MIME_TYPES=["application/pdf", "text/plain", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]

UPLOAD_DIR="storage/uploads"
PROJECT_DOCUMENTS_DIR="documents"
```

The private `.env` file can contain the same values locally.

Do not commit `.env`.

---

## 🧩 DocumentService Responsibility

`DocumentService` is responsible for upload intelligence.

It handles:

- file MIME type validation
- file size validation
- original filename cleaning
- document ID generation
- stored filename generation
- final file path preparation
- coordination with `ProjectService`

It does not directly expose absolute server paths in API responses.

---

## 🗂️ ProjectService Responsibility

`ProjectService` is responsible for project storage.

It handles:

- `project_id` validation
- project path resolution
- documents folder resolution
- folder creation when needed

Target folder:

```text
storage/uploads/{project_id}/documents/
```

---

## 🔐 Security Rules Applied

This branch follows two important backend security principles.

### Do Not Trust

Do not blindly trust:

- uploaded filenames
- uploaded MIME types
- uploaded file sizes
- project IDs
- user input

### Do Not Expose

Do not expose:

- absolute server paths
- raw server errors
- `.env` values
- internal infrastructure paths

---

## 🧪 Tests Performed

This branch was tested with Postman.

### Tested successfully

- Upload endpoint appears in Swagger
- Postman sends form-data file correctly
- Valid file upload works
- Project-based folder is created
- File is stored under the correct project folder
- File size validation works
- Controlled response signal is returned
- No absolute internal path is exposed

### Important Postman correction

If FastAPI returns:

```json
{
  "detail": [
    {
      "loc": ["body", "file"],
      "msg": "Field required"
    }
  ]
}
```

It means the form-data key is missing or incorrect.

Correct key:

```text
file
```

---

## ✅ Definition of Done

This branch is complete when:

- `POST /api/v1/documents/upload/{project_id}` works
- uploaded files are saved under `storage/uploads/{project_id}/documents/`
- file size validation works
- file type validation works
- stored filenames are safe and unique
- upload response returns clean metadata
- internal absolute paths are not exposed
- Swagger displays the upload endpoint
- Postman upload works using key `file`

---

## 🧾 Recommended Commit

```bash
git add .
git commit -m "feat: add document upload endpoint"
git push -u origin HEAD
```

If `.env` appears in `git status`, do not commit it.

---

## 🔀 Pull Request Summary

Suggested PR title:

```text
feat: add document upload endpoint
```

Suggested PR description:

```markdown
## Summary

This pull request adds the first real document upload endpoint to RAGForge.

## Changes

- Added `DocumentService` for file validation and upload path generation.
- Added `documents_router`.
- Added `POST /api/v1/documents/upload/{project_id}`.
- Integrated `ProjectService` to store uploaded files inside project-based folders.
- Added async chunked writing with `aiofiles`.
- Added file size validation.
- Added controlled API responses using `ResponseSignal`.
- Prevented internal absolute paths from being exposed in API responses.

## Tested

- Successful upload with valid file.
- File size exceeded validation.
- Project-based folder creation.
- Postman form-data upload using key `file`.
```

---

## ⏭️ Next Step

After this branch is merged, Milestone 3 has a complete first document upload foundation.

The next major milestone should move toward:

```text
Milestone 4 — Database & Document Models
```

Possible next work:

- create project model
- create document model
- store document metadata in PostgreSQL
- track upload status
- track processing status
- connect document IDs to database records
