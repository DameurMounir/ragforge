# Milestone 4 — Database Metadata & Indexing

## 🎯 Objective

Milestone 4 introduces the first database-backed metadata and indexing layer for RAGForge.

After building the document upload and processing foundation in Milestone 3, this milestone adds MongoDB infrastructure, metadata schemes, MongoDB store classes, and metadata indexes required to track projects, assets, and extracted chunks.

The goal is to move RAGForge from a file-based ingestion pipeline toward a metadata-driven RAG backend ready for persistence, indexing, semantic search, and augmented generation.

---

## 🧭 Why This Milestone Matters

A production RAG system cannot rely only on files saved on disk.

It needs a metadata layer capable of tracking:

- projects
- uploaded assets
- asset type and status
- processing state
- extracted chunks
- chunk ownership
- metadata persistence
- metadata indexing
- future semantic search readiness

This milestone prepares RAGForge for later stages such as chunk persistence, embeddings, vector search, semantic retrieval, citations, and augmented answer generation.

---

## 🧱 Architecture Direction

The core database relationship introduced in this milestone is:

```text
Project
  ↓
Asset
  ↓
DataChunk
```

A project represents a logical workspace.

An asset represents a knowledge source attached to a project.

A data chunk represents a text unit extracted from an asset.

This structure keeps RAGForge flexible because an asset can represent more than a local document file.

Examples of future asset types include:

```text
PDF file
TXT file
DOCX file
URL
web page
image
video
audio
transcript
API source
```

---

## 🧩 Production Design Principles

Milestone 4 follows these principles:

```text
1. Keep database schemes separate from API routes.
2. Keep MongoDB operations inside store classes.
3. Keep business workflow logic inside services.
4. Keep route handlers thin and focused.
5. Track assets before creating chunks.
6. Link every chunk to both project and asset.
7. Add metadata indexes before relying on large-scale queries.
8. Prepare metadata for future semantic search and augmented answers.
```

The intended flow is:

```text
routes
  ↓
services
  ↓
stores
  ↓
db_schemes
  ↓
MongoDB
```

---

## 🌿 Branch Plan

| Branch | Name | Purpose | Status |
|---|---|---|---|
| 9 | Docker MongoDB Motor Infrastructure | Add MongoDB service, configuration, dependencies, and async connection foundation | Done |
| 10 | Asset Metadata Schemes & Stores | Add database schemes and MongoDB store classes for projects, assets, and chunks | In Progress |
| 11 | MongoDB Metadata Indexes | Add MongoDB index definitions and initialization for projects, assets, and chunks | Planned |
| 12 | Upload and Processing Metadata Persistence | Connect upload and processing endpoints to MongoDB metadata persistence | Planned |

---

## 📦 Branch 9 — Docker MongoDB Motor Infrastructure

Branch 9 introduced the MongoDB infrastructure layer.

It prepared the backend to connect to MongoDB asynchronously and added the foundation required for future metadata persistence.

Main focus:

```text
MongoDB Docker service
MongoDB environment configuration
MongoDB Python dependency
Async database connection foundation
MongoDB store folder structure
```

---

## 📦 Branch 10 — Asset Metadata Schemes & Stores

Branch 10 introduces the first metadata scheme and store layer.

It defines how RAGForge represents projects, assets, and chunks at the database level.

Main focus:

```text
Project scheme
Asset scheme
DataChunk scheme
Asset type enum
Asset status enum
MongoDB collection enum
Base MongoDB store
Project store
Asset store
Chunk store
```

This branch does not initialize MongoDB indexes. Indexing is intentionally kept for Branch 11.

---

## 📦 Branch 11 — MongoDB Metadata Indexes

Branch 11 will add database indexes for the metadata layer.

Main focus:

```text
Project indexes
Asset indexes
DataChunk indexes
Index initialization logic
Database query readiness
```

Expected indexes include:

```text
project_id unique index
asset_project_id index
asset project/name index
asset status index
chunk_project_id index
chunk_asset_id index
chunk order index
```

This branch will improve query performance and prepare the system for larger datasets.

---

## 📦 Branch 12 — Upload and Processing Metadata Persistence

Branch 12 will connect the existing upload and processing pipeline to MongoDB metadata persistence.

Expected flow:

```text
Upload endpoint
  ↓
create project if needed
  ↓
create asset record
  ↓
processing endpoint updates asset status
  ↓
chunks are saved and linked to the asset
```

This branch will make the metadata layer active in the real ingestion workflow.

---

## 🚫 Out of Scope for This Milestone

This milestone does not include:

- embedding generation
- vector database integration
- semantic search endpoint
- LLM answer generation
- citation-aware responses
- RAG evaluation
- production deployment

Those belong to later milestones.

---

## ✅ Milestone Definition of Done

This milestone is complete when:

- MongoDB infrastructure is available
- MongoDB connection foundation is implemented
- project database scheme exists
- asset database scheme exists
- data chunk database scheme exists
- MongoDB store classes exist
- metadata indexes are initialized
- upload metadata can be persisted
- processing results can update metadata records
- chunks can be linked to projects and assets
- existing tests pass
- documentation is updated
