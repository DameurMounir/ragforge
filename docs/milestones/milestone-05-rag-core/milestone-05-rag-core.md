# Milestone 5 — RAG Core: LLM, Vector Store & Retrieval

## Objective

Milestone 5 starts the real RAG Core of RAGForge.

Previous milestones built the backend foundation, document upload, document processing, MongoDB metadata, indexes, and the metadata-driven ingestion pipeline.

Milestone 5 moves RAGForge from a stable ingestion backend to an intelligent RAG system.

The goal is to add the core intelligence layers step by step:

```text
Project
  ↓
Asset
  ↓
DataChunk
  ↓
LLM Factory
  ↓
Vector Store
  ↓
Embeddings
  ↓
Semantic Search
  ↓
Grounded Answers with Sources
```

## Architectural Principle

Milestone 5 must keep RAGForge modular and provider-neutral.

RAGForge must not be locked to one LLM provider, one vector database, one embedding backend, or one retrieval strategy.

The architecture must continue to follow:

```text
Route
  ↓
Service
  ↓
Factory / Provider / Store
  ↓
External System
```

This keeps each layer replaceable, testable, and ready for production evolution.

---

## Milestone 5 Branches

| Branch | Name | Main Goal |
|---|---|---|
| 14 | LLM Factory | Create a provider-neutral interface for LLM clients and response generation. |
| 15 | Vector DB Factory | Create vector database abstraction and configuration. |
| 16 | Embeddings & Indexing | Generate embeddings from chunks and store vectors with metadata. |
| 17 | Semantic Search | Search indexed chunks by similarity and return ranked evidence. |
| 18 | Augmented Answers with Sources | Generate answers grounded in retrieved chunks with source metadata. |
| 19 | RAG Core Stabilization + Local LLM Option | Stabilize the full RAG workflow and support local LLM options. |

---

## Branch 14 — LLM Factory

Branch 14 introduces the first RAG Core component: the LLM generation layer.

It adds:

- LLM provider enum
- LLM request and response schemas
- LLM exceptions
- Base LLM provider interface
- Fake LLM provider
- OpenAI-compatible LLM provider
- LLM provider factory
- LLM service
- `/api/v1/llm/generate` endpoint
- Unit tests
- Validation script
- API documentation

Branch 14 does not include:

- vector database
- embeddings
- semantic search
- RAG answer generation with sources
- agents

---

## Branch 15 — Vector DB Factory

Branch 15 will introduce the vector database abstraction.

Expected goal:

```text
RAGForge should be able to create and configure a vector store provider without coupling the system to one database.
```

Possible future providers:

- Qdrant
- PgVector
- FAISS
- Chroma

Branch 15 should not generate embeddings yet. It only prepares the vector database layer.

---

## Branch 16 — Embeddings & Indexing

Branch 16 will introduce embeddings and indexing.

Expected goal:

```text
Take persisted DataChunks and transform them into vectors stored with metadata.
```

Expected flow:

```text
MongoDB DataChunks
  ↓
Embedding Provider
  ↓
Vector Store
  ↓
Indexed vectors with metadata
```

This branch should connect chunks to vectors while preserving project, asset, and chunk metadata.

---

## Branch 17 — Semantic Search

Branch 17 will introduce semantic retrieval.

Expected goal:

```text
Given a user query, retrieve the most relevant chunks from the vector store.
```

Expected response should include ranked evidence:

- chunk id
- asset id
- project id
- similarity score
- text preview
- metadata

---

## Branch 18 — Augmented Answers with Sources

Branch 18 will connect retrieval with the LLM Factory.

Expected flow:

```text
User question
  ↓
Semantic Search
  ↓
Retrieved chunks
  ↓
Prompt construction
  ↓
LLM Factory
  ↓
Grounded answer with sources
```

The answer must be grounded in retrieved evidence and return source metadata.

---

## Branch 19 — RAG Core Stabilization + Local LLM Option

Branch 19 will stabilize the complete RAG Core.

Expected work:

- improve errors
- improve configuration
- add local LLM option
- improve tests
- improve documentation
- validate the full RAG Core workflow

---

## Milestone 5 Definition of Done

Milestone 5 is complete when RAGForge can:

1. Generate text through a provider-neutral LLM Factory.
2. Configure a vector database through a provider-neutral factory.
3. Generate embeddings from persisted chunks.
4. Store vectors with project, asset, and chunk metadata.
5. Run semantic search against indexed chunks.
6. Generate grounded answers using retrieved evidence.
7. Return answer sources.
8. Support at least one external LLM provider.
9. Prepare support for at least one local LLM-compatible provider.
10. Pass all validation scripts and tests.

---

## Milestone 5 Boundary

Milestone 5 is still focused on the RAG Core.

It does not introduce:

- Celery workers
- deployment hardening
- observability dashboard
- RBAC/JWT
- agent orchestration
- OS agents

Those belong to later production and agent-ready milestones.
