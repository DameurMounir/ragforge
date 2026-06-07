# Branch 21 — PgVector Provider & PostgreSQL Vector Backend

Git branch:

```text
feature/21-pgvector-provider-indexing
```

Milestone:

```text
Milestone 6 — Production Deployment & Workers
```

## Goal

Add **PgVector** as a first-class vector database backend while preserving **Qdrant** compatibility and the existing RAG Core flow.

Branch 21 upgrades RAGForge from a single active vector backend implementation to a provider-switchable vector architecture where the same indexing, search, and answer-generation services can run on either Qdrant or PostgreSQL/PgVector.

## Why this branch exists

Branch 20 introduced the PostgreSQL production persistence foundation:

- PostgreSQL Docker service,
- PgVector-capable PostgreSQL image,
- SQLAlchemy async ORM,
- Alembic migrations,
- session management,
- repository layer,
- domain record mapping,
- Unit of Work transaction policy.

Branch 21 connects that PostgreSQL foundation to the existing vector database abstraction used by:

```text
IndexingService
SemanticSearchService
RAGAnswerService
```

The branch makes PgVector usable as a real vector backend for indexing, semantic search, and grounded answer generation.

## Architecture

```text
IndexingService / SemanticSearchService
  ↓
VectorDBService
  ↓
VectorDBProviderFactory
  ↓
BaseVectorDBProvider
  ├── QdrantProvider
  └── PgVectorProvider
        ↓
      PostgresSessionManager
        ↓
      vector_records table
        ↓
      PgVector provider-managed index
```

The vector provider boundary remains provider-neutral. Services do not know whether the active backend is Qdrant or PgVector.

The active backend is selected by configuration:

```env
VECTOR_DB_PROVIDER="pgvector"
```

or:

```env
VECTOR_DB_PROVIDER="qdrant"
```

MongoDB remains responsible for project, asset, and chunk metadata in the current ingestion path. PgVector is used for vector indexing and vector similarity search.

## Main changes

- Add PgVector provider implementation.
- Add PgVector configuration settings.
- Add `VectorDBProvider.PGVECTOR` enum value.
- Upgrade the vector DB provider boundary to async.
- Keep Qdrant supported through async provider methods.
- Add missing Qdrant async compatibility methods.
- Add Alembic migration for the `vector_records` table.
- Add variable-dimension PgVector storage with `vector_size` validation.
- Add provider-managed HNSW / IVFFLAT expression index support.
- Keep `collection_name` as a logical namespace, not as a dynamic table name.
- Preserve existing `VectorRecord` and `VectorSearchResult` contracts.
- Preserve service-level compatibility for indexing and semantic search.
- Add PgVector validation script.
- Add provider contract tests.
- Add SQL safety tests.
- Add vector-size configuration tests.
- Add PgVector similarity scoring tests.
- Add semantic search tests against PgVector backend.
- Add async contract tests for Qdrant and PgVector.

## PgVector table design

Branch 21 uses one Alembic-managed table:

```text
vector_records
```

It does **not** create one table per project or one table per collection.

`collection_name` is treated as a logical namespace inside the table.

This keeps the database schema stable and avoids unsafe dynamic table creation.

The vector storage model supports:

```text
collection_name
record_id
vector
vector_size
text
metadata
embedding_model
created_at
updated_at
```

## PgVector indexing strategy

Branch 21 supports provider-managed vector indexes for the configured dimension and distance method.

Supported index types:

```text
hnsw
ivfflat
```

Supported index vector expression types:

```text
vector
halfvec
```

Supported distance methods:

```text
cosine
euclid
dot
```

Default production-oriented configuration:

```env
PGVECTOR_INDEX_TYPE="hnsw"
PGVECTOR_INDEX_VECTOR_TYPE="vector"
PGVECTOR_DISTANCE="cosine"
PGVECTOR_AUTO_CREATE_INDEX=true
PGVECTOR_CREATE_EXTENSION_ON_STARTUP=true
```

## Configuration

Minimum PgVector runtime configuration:

```env
VECTOR_DB_PROVIDER="pgvector"
VECTOR_DB_COLLECTION_NAME="ragforge_chunks"
VECTOR_DB_VECTOR_SIZE=1536
VECTOR_DB_DISTANCE="cosine"

PGVECTOR_TABLE_NAME="vector_records"
PGVECTOR_DISTANCE="cosine"
PGVECTOR_INDEX_TYPE="hnsw"
PGVECTOR_INDEX_VECTOR_TYPE="vector"
PGVECTOR_HNSW_M=16
PGVECTOR_HNSW_EF_CONSTRUCTION=64
PGVECTOR_HNSW_EF_SEARCH=40
PGVECTOR_INDEX_MIN_RECORDS=0
PGVECTOR_AUTO_CREATE_INDEX=true
PGVECTOR_CREATE_EXTENSION_ON_STARTUP=true
```

Embedding vector size remains controlled by:

```env
EMBEDDING_VECTOR_SIZE=1536
```

`VECTOR_DB_VECTOR_SIZE`, `QDRANT_VECTOR_SIZE`, and `PGVECTOR_VECTOR_SIZE` are optional equality guards. If set, they must match `EMBEDDING_VECTOR_SIZE`.

## Real OpenAI + PgVector validation configuration

The real end-to-end validation used:

```env
VECTOR_DB_PROVIDER="pgvector"
VECTOR_DB_COLLECTION_NAME="ragforge_chunks"

EMBEDDING_PROVIDER="openai_compatible"
EMBEDDING_MODEL="text-embedding-3-small"
EMBEDDING_VECTOR_SIZE=1536
EMBEDDING_OPENAI_BASE_URL="https://api.openai.com/v1"

LLM_PROVIDER="openai_compatible"
LLM_DEFAULT_MODEL="gpt-4o-mini"
OPENAI_BASE_URL="https://api.openai.com/v1"
```

Private API keys must stay in local `.env` files and must never be committed.

## Validation commands

Run infrastructure:

```bash
docker compose --env-file .env -f docker/docker-compose.yml up -d
```

Check PostgreSQL readiness:

```bash
docker compose --env-file .env -f docker/docker-compose.yml ps
docker exec -it ragforge-postgres pg_isready -U ragforge -d ragforge
```

Run Alembic:

```bash
alembic -c alembic.ini upgrade head
alembic -c alembic.ini current
```

Expected migration head:

```text
20260606_0002 (head)
```

Compile:

```bash
python -m compileall src/ragforge migrations scripts/validation tests
```

Run PgVector validation:

```bash
python scripts/validation/validate_branch_21_pgvector_provider.py
```

Expected validation output:

```text
PostgreSQL ping succeeded.
PgVector extension exists.
vector_records table exists.
Configured PgVector index exists.
PgVector insert_many succeeded.
PgVector search_by_vector succeeded.
Branch 21 PgVector provider validation passed.
```

Run Branch 21 tests:

```bash
pytest tests/branch_21_pgvector -q
```

Expected result:

```text
46 passed
```

Run the full test suite:

```bash
pytest -q
```

Expected result after Branch 21 fixes:

```text
93 passed
```

## Real end-to-end Postman validation

Branch 21 was also validated through Postman with the real runtime pipeline:

```text
Postman Client
  ↓
FastAPI API
  ↓
MongoDB metadata and chunks
  ↓
OpenAI text-embedding-3-small embeddings
  ↓
PostgreSQL + pgvector vector storage
  ↓
Semantic search from PgVector
  ↓
Retrieval post-processing
  ↓
GPT-4o-mini grounded answer generation
  ↓
Citation validation
```

Validated API flow:

```text
GET  /api/v1/health/
POST /api/v1/documents/upload/{project_id}
POST /api/v1/documents/process/{project_id}
POST /api/v1/indexing/{project_id}
POST /api/v1/search/{project_id}
POST /api/v1/answers/{project_id}
```

Validated answer response included:

```text
signal = rag_answer_success
embedding_model = text-embedding-3-small
embedding_provider = openai_compatible
llm_model = gpt-4o-mini
retrieval_count = 3
citation_validation.invalid_source_numbers = []
citation_validation.was_modified = false
```

This confirms that Branch 21 is not only unit-tested. It was validated as a real OpenAI + PgVector + MongoDB RAG pipeline.

## Retrieval behavior observed during validation

The real Postman validation demonstrated that RAGForge does not blindly pass arbitrary chunks to the LLM.

The answer pipeline retrieved candidates, applied post-processing, selected the strongest evidence, applied dominant-asset logic when appropriate, limited chunks per asset, and validated citations.

Observed diagnostics included:

```text
candidate_count = 20
removed_below_min_score = 0.25
removed_by_asset_limit = 7
dominant_asset_applied = true
final_count = 3
```

This confirms that the retrieval layer already contains strategy beyond naive top-k chunk dumping.

## Manual PgVector database check

After indexing, verify vector rows directly in PostgreSQL:

```bash
docker exec -it ragforge-postgres psql -U ragforge -d ragforge -c "
select collection_name, embedding_model, count(*)
from vector_records
group by collection_name, embedding_model;
"
```

Expected shape:

```text
collection_name | embedding_model          | count
ragforge_chunks | text-embedding-3-small   | ...
```

## Switching between Qdrant and PgVector

Use PgVector:

```env
VECTOR_DB_PROVIDER="pgvector"
```

Use Qdrant:

```env
VECTOR_DB_PROVIDER="qdrant"
```

After changing the provider, restart the API and re-index:

```bash
pkill -f "uvicorn src.ragforge.main:app" || true
uvicorn src.ragforge.main:app --host 127.0.0.1 --port 8000
```

Then:

```bash
curl -s -X POST "$BASE/indexing/$PROJECT_ID" \
  -H "Content-Type: application/json" \
  -d '{"do_reset":true}' \
  | python -m json.tool
```

MongoDB remains used in both modes for project, asset, and chunk metadata. Only the vector backend changes.

## Definition of done

- PostgreSQL is reachable.
- PgVector extension exists.
- `vector_records` table exists.
- Configured PgVector index exists.
- PgVector provider can insert vectors.
- PgVector provider can search vectors.
- Search results are returned in the same normalized shape as Qdrant.
- Qdrant provider remains supported.
- Factory can switch between `qdrant` and `pgvector`.
- Vector provider boundary is async.
- Indexing works with PgVector.
- Semantic search works with PgVector.
- Grounded answer generation works with PgVector retrieval.
- Real OpenAI embeddings work with PgVector.
- Real OpenAI LLM answer generation works from retrieved PgVector evidence.
- Postman end-to-end validation passes.
- Full test suite passes.

## Final validation summary

Branch 21 validates the following production-oriented RAG path:

```text
Upload document
  ↓
Persist metadata in MongoDB
  ↓
Process document into DataChunk records
  ↓
Generate OpenAI embeddings
  ↓
Store vectors in PostgreSQL using pgvector
  ↓
Search vectors through PgVectorProvider
  ↓
Post-process retrieved evidence
  ↓
Generate grounded GPT-4o-mini answer
  ↓
Validate citations
```

Branch 21 confirms that RAGForge can use PostgreSQL/PgVector as a real vector backend while preserving the provider architecture needed for future vector database backends.
