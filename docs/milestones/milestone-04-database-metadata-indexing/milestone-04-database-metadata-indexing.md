# Milestone 4 — Database Metadata & Indexing & Auth

## 🎯 Objective

Milestone 4 introduces the first database-backed metadata, indexing, and authenticated MongoDB layer for RAGForge.

After building the document upload and processing foundation in Milestone 3, this milestone adds MongoDB infrastructure, metadata schemes, MongoDB store classes, metadata indexes, MongoDB authentication, and metadata persistence validation for projects, assets, and extracted chunks.

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


This milestone prepares RAGForge for later stages such as chunk persistence, embeddings, vector search, 
semantic retrieval, citations, and augmented answer generation.
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

---

## 🧩 Production Design Principles

```text
1. Keep database schemes separate from API routes.
2. Keep MongoDB operations inside store classes.
3. Keep business workflow logic inside services.
4. Keep route handlers thin and focused.
5. Track assets before creating chunks.
6. Link every chunk to both project and asset.
7. Add metadata indexes before relying on large-scale queries.
8. Use authenticated database access for realistic local development.
9. Prepare metadata for future semantic search and augmented answers.
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
| 10 | Asset Metadata Schemes & Stores | Add database schemes and MongoDB store classes for projects, assets, and chunks | Done |
| 11 | MongoDB Metadata Indexes & Auth | Add MongoDB index definitions, initialization logic, and authenticated MongoDB access | Done |
| 12 | Upload and Processing Metadata Persistence | Validate MongoDB persistence for projects, assets, and chunks | In Progress |

---

## 📦 Branch 9 — Docker MongoDB Motor Infrastructure

Branch 9 introduced the MongoDB infrastructure layer.

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

Branch 10 introduced the first metadata scheme and store layer.

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

---

## 📦 Branch 11 — MongoDB Metadata Indexes & Auth

Branch 11 added database indexes and authenticated MongoDB access.

Main focus:

```text
Project indexes
Asset indexes
DataChunk indexes
Index initialization logic
Database query readiness
MongoDB authentication through Docker Compose
Authenticated MongoDB connection string
Environment example files
```

---

## 📦 Branch 12 — Upload and Processing Metadata Persistence

Branch 12 validates the metadata persistence layer across MongoDB stores.

Main focus:

```text
Project creation and reuse
Asset creation and reuse
Uploaded asset retrieval
Chunk insertion
Chunk retrieval by asset
Asset status update
Asset chunk count update
Project identifier validation with underscores and hyphens
Validation utility script
```

Validated relationship:

```text
ProjectStore → AssetStore → ChunkStore
```

Branch 12 confirms that the metadata layer can persist and update real MongoDB records before the persistence logic is connected to the API workflow.

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

---

## ✅ Milestone Definition of Done

This milestone is complete when:

- MongoDB infrastructure is available
- MongoDB connection foundation is implemented
- MongoDB authenticated local access works
- project database scheme exists
- asset database scheme exists
- data chunk database scheme exists
- MongoDB store classes exist
- metadata indexes are initialized
- project metadata can be persisted
- asset metadata can be persisted
- chunks can be linked to projects and assets
- asset processing metadata can be updated
- existing tests pass
- documentation is updated
