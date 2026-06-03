# Branch 15 — Vector DB Factory with Qdrant

## Milestone

**Milestone 5 — RAG Core: LLM, Vector Store & Retrieval**

## Branch

```text
feature/15-vector-db-factory-qdrant
```

## Goal

Add a **provider-neutral vector database layer** with **Qdrant** as the first concrete implementation.

This branch prepares RAGForge to store and search vectors, but it deliberately stays limited to the vector database infrastructure layer.

It does **not** generate embeddings and does **not** index MongoDB chunks yet.

## Architectural Decision

RAGForge continues the professional provider-based architecture introduced in Branch 14:

```text
Route → Service → Provider Interface → Provider Implementation
```

Branch 15 extends this pattern to vector databases.

The goal is to keep RAGForge independent from one specific vector database vendor. Qdrant is the first implementation, but the architecture remains open for future providers such as Pinecone, Weaviate, pgvector, Milvus, or an in-memory test provider.

## Docker Decision

Qdrant runs through **Docker Compose** by default.

This is the professional development and production-aligned choice because it keeps the vector database isolated, reproducible, and easy to replace or upgrade.

The provider also supports local embedded mode for tests and lightweight prototyping when needed.

## Dependency Added

```text
qdrant-client==1.18.0
```

Branch 15 uses the modern Qdrant Python client Query API:

```text
QdrantClient.query_points()
```

The old `client.search()` API is not used.

## Why This Branch Matters

Before building semantic search, RAGForge needs a clean vector storage layer.

This branch creates that foundation by separating:

- application logic,
- vector database interface,
- provider selection,
- Qdrant implementation,
- validation scripts,
- and tests.

This makes future branches easier, safer, and more professional.

## Added Components

Branch 15 adds:

- Base vector DB provider interface
- Vector DB provider enum
- Vector DB exceptions
- Vector record and search schemas
- Qdrant provider implementation
- Vector DB provider factory
- Vector DB service
- Docker Qdrant service
- Validation script with fake vectors
- Unit tests for the factory

## Created Files

```text
src/ragforge/providers/vector_db/
├── __init__.py
├── base.py
├── enums.py
├── exceptions.py
├── factory.py
├── schemas.py
└── implementations/
    ├── __init__.py
    └── qdrant_provider.py

src/ragforge/services/vector_db_service.py
scripts/validation/validate_branch_15_vector_db.py
tests/test_vector_db_factory.py
```

## Updated Files

```text
requirements.txt
.env.example
src/ragforge/core/config.py
docker/docker-compose.yml
.gitignore
README.md
docs/milestones/milestone-05-rag-core/milestone-05-rag-core.md
docs/setup/local-development.md
```

## Not Included in This Branch

Branch 15 does **not** include:

- embedding generation,
- MongoDB chunk indexing,
- semantic search endpoint,
- grounded answer generation,
- agent layer,
- advanced retrieval strategies,
- reranking,
- hybrid search.

These features belong to later Milestone 5 branches.

## Scope Boundary

Branch 15 is only responsible for the vector database infrastructure.

```text
MongoDB chunks exist already.
LLM provider layer exists already.
Qdrant vector storage is added now.
Embeddings and indexing come next.
```

## Expected Architecture After Branch 15

```text
RAGForge Application
│
├── Services
│   └── VectorDBService
│
├── Provider Factory
│   └── VectorDBProviderFactory
│
├── Provider Interface
│   └── BaseVectorDBProvider
│
└── Provider Implementation
    └── QdrantProvider
        └── Qdrant Docker Service
```

## Qdrant Runtime

Qdrant is started with Docker Compose:

```bash
docker compose --env-file .env -f docker/docker-compose.yml up -d
```

Check containers:

```bash
docker compose --env-file .env -f docker/docker-compose.yml ps
```

Expected containers:

```text
ragforge-mongodb   Running
ragforge-qdrant    Running
```

Check Qdrant:

```bash
curl http://localhost:6333/healthz
```

Alternative check:

```bash
curl http://localhost:6333
```

## Validation Script

Run:

```bash
python scripts/validation/validate_branch_15_vector_db.py
```

The validation script verifies that RAGForge can:

- connect to Qdrant,
- create a validation collection,
- insert one vector,
- insert multiple vectors,
- search by vector similarity using `query_points()`,
- return normalized search results,
- delete the validation collection.

## Successful Validation Output

```text
Connecting to vector DB...
Qdrant connection OK
Creating validation collection...
Collection created: True
Inserting one vector...
Inserted one vector
Inserting batch vectors...
Inserted batch vectors: 2
Searching by vector...
Search returned 3 result(s)
1. record_id=branch15_single_record | score=1.0 | text=RAGForge Branch 15 single validation vector.
2. record_id=branch15_batch_record_1 | score=0.999896 | text=RAGForge Branch 15 batch validation vector 1.
3. record_id=branch15_batch_record_2 | score=0.35856858 | text=A different validation vector for search comparison.
Deleting validation collection...
Collection deleted: True
Branch 15 validation passed
```

## Tests

Run Branch 15 factory test:

```bash
pytest tests/test_vector_db_factory.py -q
```

Run all tests:

```bash
pytest
```

## Definition of Done

Branch 15 is complete when:

- [x] Qdrant starts with Docker Compose.
- [x] Qdrant is reachable on `localhost:6333`.
- [x] `qdrant-client==1.18.0` is installed.
- [x] Vector DB configuration is loaded from settings.
- [x] Vector DB factory returns the Qdrant provider.
- [x] Qdrant provider can create collections.
- [x] Qdrant provider can delete collections.
- [x] Qdrant provider can insert one vector.
- [x] Qdrant provider can insert many vectors.
- [x] Qdrant provider can search by vector similarity using `query_points()`.
- [x] Validation script passes.
- [ ] Tests pass.
- [ ] README is updated.
- [ ] Milestone 5 documentation is updated.

## Professional Notes

This branch should remain small and focused.

Do not connect it directly to the document processing pipeline yet. That connection belongs to Branch 16, where embeddings will be generated from stored chunks and persisted into Qdrant with metadata.

The current branch gives RAGForge a clean vector database layer without mixing responsibilities.

## Next Branch

**Branch 16 — Embeddings & Indexing**

Branch 16 will use:

- MongoDB chunks created by the ingestion pipeline,
- the embedding provider created in Branch 14,
- the vector database provider created in Branch 15,
- and a new indexing service to persist vectors into Qdrant.
