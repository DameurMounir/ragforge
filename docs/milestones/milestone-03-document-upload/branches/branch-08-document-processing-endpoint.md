# Branch 8 — Document Processing Endpoint

## Branch Information

| Item | Value |
|---|---|
| Milestone | Milestone 3 — Document Upload & Processing Pipeline |
| Branch number | Branch 8 |
| Git branch | `feature/8-document-processing-endpoint` |
| Issue title | `Add document processing endpoint` |
| PR title | `Milestone 3: Add Document Processing Endpoint` |
| Status | Completed |

---

## Objective

This branch adds the document processing endpoint to RAGForge.

After a document is uploaded and stored inside a project folder, the API can process that document, extract its text content, split it into chunks, and return structured JSON.

The completed flow is:

```text
Upload document
→ Store document by project
→ Process uploaded document
→ Extract text
→ Split text into chunks
→ Return structured chunks
```

---

## Why This Branch Matters

A RAG system cannot work directly with raw uploaded files.

Before adding embeddings, vector databases, semantic search, or LLM answer generation, uploaded documents must first be transformed into smaller text chunks.

This branch prepares RAGForge for the next stages:

- document metadata persistence
- chunk storage
- embeddings
- vector indexing
- semantic retrieval
- grounded answer generation

---

## RAGForge Approach

This branch follows the RAGForge service-based backend architecture.

The route is responsible only for receiving the request and returning the response. The processing logic is isolated inside a dedicated service.

The processing flow is:

```text
Route
→ Schema
→ Service
→ Response
```

This keeps the API layer thin and makes the processing logic easier to test, extend, and reuse in later milestones.

---

## Architecture Decision

Upload logic and processing logic are separated.

```text
DocumentService
→ validates uploaded files
→ cleans filenames
→ generates document_id
→ generates stored_filename
→ prepares the upload path
```

```text
DocumentProcessingService
→ locates uploaded documents
→ detects file type
→ loads document content
→ splits content into chunks
→ returns JSON-ready chunks
```

This separation keeps the backend clean and prepares the project for future database persistence, background jobs, embeddings, and vector indexing.

---

## Files Added

```text
src/ragforge/services/document_processing_service.py
src/ragforge/schemas/document_processing.py
src/ragforge/models/enums/processing_file_type.py
docs/milestones/milestone-03-document-upload/branches/branch-08-document-processing-endpoint.md
```

---

## Files Modified

```text
src/ragforge/routes/documents.py
src/ragforge/models/enums/response_signals.py
src/ragforge/models/__init__.py
requirements.txt
docs/api/endpoints.md
docs/milestones/milestone-03-document-upload/milestone-03-document-upload.md
README.md
```

---

## Endpoint Added

### Process Uploaded Document

```http
POST /api/v1/documents/process/{project_id}
```

Example:

```http
POST /api/v1/documents/process/project_003
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
|---|---:|---:|---|
| `stored_filename` | string | Yes | The real stored filename returned by the upload endpoint |
| `chunk_size` | integer | No | Maximum size of each text chunk |
| `overlap_size` | integer | No | Number of overlapping characters between chunks |
| `do_reset` | boolean | No | Reserved for future re-processing logic |

---

## Important Note About `stored_filename`

The process endpoint uses `stored_filename`, not only `document_id`.

During upload, RAGForge stores documents using this format:

```text
storage/uploads/{project_id}/documents/{document_id}_{clean_filename}
```

Example:

```text
storage/uploads/project_003/documents/eaf4a826-821b-43c5-b544-5863abecff1a_intro_ragforg.txt
```

Because there is no database yet, the safest way to process the file is to pass the full `stored_filename`.

---

## Successful Response Example

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

## Response Signals Added

```text
DOCUMENT_NOT_FOUND
DOCUMENT_PROCESSING_SUCCESS
DOCUMENT_PROCESSING_FAILED
DOCUMENT_TYPE_NOT_SUPPORTED
DOCUMENT_EMPTY_CONTENT
```

These signals make the API response clearer and prepare the project for consistent error handling across future milestones.

---

## Processing Flow

```text
Client
↓
POST /api/v1/documents/process/{project_id}
↓
documents.py
↓
ProcessDocumentRequest
↓
DocumentProcessingService
↓
ProjectService
↓
Uploaded document path
↓
TextLoader / PyMuPDFLoader
↓
RecursiveCharacterTextSplitter
↓
JSON chunks response
```

---

## Supported Processing Types

| Extension | Loader |
|---|---|
| `.txt` | `TextLoader` |
| `.pdf` | `PyMuPDFLoader` |

DOCX upload may be allowed by configuration, but DOCX processing is not included in this branch.

DOCX support can be added later with a dedicated loader.

---

## Dependencies Added

```text
langchain-community
langchain-text-splitters
pymupdf
```

These packages are used for document loading and chunking.

---

## Postman Test

### Step 1 — Upload Document

```http
POST /api/v1/documents/upload/project_003
```

Body:

```text
form-data
file → intro_ragforg.txt
```

Expected response:

```json
{
  "signal": "file_upload_success",
  "message": "Document uploaded successfully.",
  "document_id": "eaf4a826-821b-43c5-b544-5863abecff1a",
  "project_id": "project_003",
  "original_filename": "intro_ragforg.txt",
  "stored_filename": "eaf4a826-821b-43c5-b544-5863abecff1a_intro_ragforg.txt"
}
```

### Step 2 — Process Document

```http
POST /api/v1/documents/process/project_003
```

Body:

```json
{
  "stored_filename": "eaf4a826-821b-43c5-b544-5863abecff1a_intro_ragforg.txt",
  "chunk_size": 1000,
  "overlap_size": 200,
  "do_reset": false
}
```

Expected result:

```text
200 OK
document_processing_success
```

---

## Completed Work

- Added processing request schema
- Added document processing service
- Added processing file type enum
- Added document processing endpoint
- Added TXT file processing
- Added PDF file processing foundation
- Added recursive character text splitting
- Added structured chunks response
- Added processing response signals
- Tested upload and processing with Postman

---

## Out of Scope

This branch does not include:

- database persistence
- document metadata table
- chunk table
- embeddings
- vector indexing
- Qdrant
- PGVector
- Celery background jobs
- LLM answer generation

These belong to later milestones.

---

## Final Result

Milestone 3 now has a complete first document ingestion pipeline.

RAGForge can:

```text
receive a document
→ validate it
→ store it safely by project
→ process it
→ split it into chunks
→ return structured chunks
```

This prepares the project for the next milestone: storing document metadata and preparing chunks for embeddings and vector search.
