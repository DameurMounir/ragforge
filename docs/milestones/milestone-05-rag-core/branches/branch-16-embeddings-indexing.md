# Branch 16 — Embeddings & Indexing Foundation

## Milestone

Milestone 5 — RAG Core: LLM, Vector Store & Retrieval

## Branch

`feature/16-embeddings-indexing`

## Status

Completed and validated.

## Goal

Add the indexing foundation that connects persisted MongoDB chunks to the vector database layer.

This branch introduces the complete path:

```text
MongoDB DataChunk
  → Embedding Provider
  → VectorRecord
  → VectorDBService
  → Qdrant collection
```

Branch 16 makes RAGForge capable of embedding stored chunks and indexing them into a vector database while keeping the architecture provider-neutral and advanced-RAG-ready.

## Architectural decision

RAGForge uses the same professional architecture pattern introduced in previous branches:

```text
Route
  → Service
  → Provider Interface
  → Provider Factory
  → Provider Implementation
```

For Branch 16, the indexing flow is:

```text
Indexing Route
  → IndexingService
  → EmbeddingProviderFactory
  → Embedding Provider
  → VectorDBService
  → VectorDBProviderFactory
  → Vector DB Provider
```

The service layer does not directly depend on Qdrant, OpenAI, or any concrete infrastructure implementation.

## No-hardcode rule

Branch 16 enforces the following professional rule:

```text
No hardcoded operational values inside services.
No hidden fallback defaults inside factories.
No provider-specific configuration names inside generic services.
All runtime values come from .env → core/config.py → settings.
```

Allowed places for defaults:

```text
.env.example
src/ragforge/core/config.py
tests
validation scripts
documentation
```

Not allowed:

```text
services
routes
provider factories
provider-neutral orchestration code
```

The final configuration flow is:

```text
.env
  → core/config.py
  → settings
  → factory/service
  → provider
```

## Current implemented strategy

Branch 16 implements simple chunk-level indexing:

```text
DataChunk → Embedding → Vector DB Point
```

This is the first production-oriented indexing strategy.

## Future-ready strategies

The architecture is prepared for later advanced indexing strategies, including:

- Late chunking
- Contextual chunking
- Asset-level vectors
- Section-level vectors
- Document-level vectors
- Hierarchical retrieval
- Parent/child retrieval
- Multi-vector retrieval

These strategies are intentionally not implemented in Branch 16.

## Added files

```text
src/ragforge/providers/embedding/__init__.py
src/ragforge/providers/embedding/base.py
src/ragforge/providers/embedding/enums.py
src/ragforge/providers/embedding/exceptions.py
src/ragforge/providers/embedding/factory.py
src/ragforge/providers/embedding/schemas.py
src/ragforge/providers/embedding/implementations/__init__.py
src/ragforge/providers/embedding/implementations/fake_embedding_provider.py
src/ragforge/providers/embedding/implementations/openai_compatible_embedding_provider.py

src/ragforge/schemas/indexing.py
src/ragforge/services/indexing_service.py
src/ragforge/routes/indexing.py

scripts/validation/validate_branch_16_indexing.py

tests/test_embedding_provider_factory.py
tests/test_indexing_schemas.py
```

## Updated files

```text
.env.example
src/ragforge/core/config.py
src/ragforge/main.py
src/ragforge/models/enums/response_signals.py
src/ragforge/stores/mongodb/chunk_store.py
src/ragforge/services/vector_db_service.py
src/ragforge/providers/vector_db/factory.py
src/ragforge/providers/llm/factory.py
README.md
```

## Embedding provider layer

Branch 16 adds a provider-neutral embedding layer.

### Interface

```text
BaseEmbeddingProvider
```

### Implementations

```text
FakeEmbeddingProvider
OpenAICompatibleEmbeddingProvider
```

### Factory

```text
EmbeddingProviderFactory
```

The fake provider is used for local validation and tests. It creates deterministic pseudo-vectors without calling any external API.

The OpenAI-compatible provider is prepared for real embedding APIs.

## Indexing schemas

Branch 16 adds indexing request and response schemas.

The request supports:

- `asset_id`
- `do_reset`
- `batch_size`
- `limit`
- `strategy`
- `granularity`
- `include_results`

Current accepted values:

```text
strategy = simple_chunk
granularity = chunk
```

Other strategies are reserved for later branches.

## Indexing service

The `IndexingService` orchestrates the full indexing workflow:

```text
1. Resolve project from ProjectStore
2. Load chunks from ChunkStore
3. Create embeddings through EmbeddingProviderFactory
4. Build VectorRecord objects
5. Insert vectors through VectorDBService
6. Mark MongoDB chunks as embedded
7. Return indexing statistics
```

The service does not perform search.

## Vector DB service cleanup

Branch 16 also cleans the vector DB service so it remains provider-neutral.

Correct generic settings:

```text
VECTOR_DB_COLLECTION_NAME
VECTOR_DB_VECTOR_SIZE
VECTOR_DB_DISTANCE
```

Generic services and routes must not reference:

```text
QDRANT_COLLECTION_NAME
QDRANT_VECTOR_SIZE
QDRANT_DISTANCE
```

Provider-specific Qdrant settings are only used inside the vector DB provider factory and Qdrant provider implementation.

## Runtime configuration

The following settings are required in `src/ragforge/core/config.py` and `.env.example`.

```env
# Generic Vector DB Indexing Configuration
VECTOR_DB_COLLECTION_NAME="ragforge_chunks"
VECTOR_DB_VECTOR_SIZE=1536
VECTOR_DB_DISTANCE="cosine"

# Embedding Configuration
EMBEDDING_PROVIDER="fake"
EMBEDDING_MODEL="text-embedding-3-small"
EMBEDDING_VECTOR_SIZE=1536
EMBEDDING_BATCH_SIZE=32
FAKE_EMBEDDING_MODEL="fake-embedding-model"

EMBEDDING_OPENAI_API_KEY=""
EMBEDDING_OPENAI_BASE_URL=""
```

Provider-specific Qdrant settings remain separate:

```env
VECTOR_DB_PROVIDER="qdrant"
QDRANT_MODE="server"
QDRANT_URL="http://localhost:6333"
QDRANT_API_KEY=""
QDRANT_LOCAL_PATH="storage/vector_db/qdrant"
QDRANT_PREFER_GRPC=false
```

## API endpoint

Branch 16 adds:

```http
POST /api/v1/indexing/{project_id}
```

Example request:

```json
{
  "asset_id": null,
  "do_reset": true,
  "batch_size": 32,
  "limit": null,
  "strategy": "simple_chunk",
  "granularity": "chunk",
  "include_results": true
}
```

Example successful response:

```json
{
  "signal": "indexing_success",
  "message": "Indexing completed.",
  "project_id": "project16test",
  "asset_id": null,
  "strategy": "simple_chunk",
  "granularity": "chunk",
  "collection_name": "ragforge_chunks",
  "embedding_model": "fake-embedding-model",
  "indexed_chunks": 1,
  "failed_chunks": 0,
  "skipped_chunks": 0
}
```

## Validation workflow

Branch 16 was validated with the full workflow:

```text
upload file
  → process file into MongoDB chunks
  → index chunks into Qdrant
  → mark chunks as embedded
  → validate indexed result
```

### Upload test file

```bash
mkdir -p tmp

cat > tmp/test1.txt <<'EOF'
RAGForge Branch 16 validates the indexing pipeline.
This file will be uploaded, processed into chunks, embedded with the fake embedding provider, and indexed into Qdrant.
EOF

curl -X POST \
  -F "file=@tmp/test1.txt" \
  http://127.0.0.1:8000/api/v1/documents/upload/project16test
```

### Process document

```bash
curl -X POST \
  http://127.0.0.1:8000/api/v1/documents/process/project16test \
  -H "Content-Type: application/json" \
  -d '{
    "asset_id": null,
    "stored_filename": null,
    "chunk_size": 1000,
    "overlap_size": 200,
    "do_reset": false,
    "include_chunks": false
  }'
```

### Index chunks

```bash
curl -X POST \
  http://127.0.0.1:8000/api/v1/indexing/project16test \
  -H "Content-Type: application/json" \
  -d '{
    "asset_id": null,
    "do_reset": true,
    "batch_size": 32,
    "limit": null,
    "strategy": "simple_chunk",
    "granularity": "chunk",
    "include_results": true
  }'
```

### Run validation script

```bash
python scripts/validation/validate_branch_16_indexing.py
```

Expected result:

```text
Branch 16 indexing validation passed
```

## Test result

```bash
pytest
```

Validated result:

```text
11 passed
```

## Architecture audit

The no-hardcode audit was performed.

### Provider-specific config leakage

```bash
grep -R "QDRANT_" -n src/ragforge/services src/ragforge/routes \
  --exclude-dir="__pycache__"
```

Expected result:

```text
no output
```

### Hidden settings fallback audit

```bash
grep -R "getattr(settings" -n src/ragforge/providers src/ragforge/services src/ragforge/routes \
  --exclude-dir="__pycache__"
```

Expected result:

```text
no output
```

## What Branch 16 does not include

Branch 16 does not include:

- Semantic search endpoint
- User query embedding
- Similarity search route
- Grounded answer generation
- Reranking
- Hybrid search
- Late chunking implementation
- Agent orchestration
- Evaluation pipeline

These responsibilities are reserved for later branches.

## Definition of done

Branch 16 is done when:

- Embedding provider interface exists
- Fake embedding provider works
- OpenAI-compatible embedding provider exists
- Embedding provider factory works without hidden fallback defaults
- Indexing request and response schemas exist
- ChunkStore can retrieve indexable project chunks
- ChunkStore can mark chunks as embedded
- IndexingService indexes chunks into the vector DB
- VectorDBService remains provider-neutral
- Indexing route is registered in FastAPI
- Tests pass
- Validation script passes
- No provider-specific config leaks into services or routes
- Runtime values come from `.env` and `core/config.py`

All conditions are satisfied.

## Next branch

Branch 17 — Semantic Search

Planned flow:

```text
User query
  → query embedding
  → vector similarity search
  → ranked evidence chunks
```

Branch 17 will use the indexing foundation created in Branch 16.
