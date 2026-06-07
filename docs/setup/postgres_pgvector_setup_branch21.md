# PostgreSQL, Alembic, and PgVector setup

Branch 21 extends the PostgreSQL production foundation introduced in Branch 20 by adding a real PgVector vector database provider for RAGForge.

Branch 21 keeps MongoDB as the ingestion metadata store and adds PostgreSQL/PgVector as an alternative vector backend to Qdrant.

## Active architecture

```text
Upload / Process
  ↓
MongoDB
  ↓
DataChunk metadata
  ↓
OpenAI or fake embeddings
  ↓
VectorDBService
  ↓
VectorDBProviderFactory
  ↓
PgVectorProvider or QdrantProvider
  ↓
Semantic Search
  ↓
Grounded Answer with Sources
```

For Branch 21 PgVector testing, the active vector backend is:

```env
VECTOR_DB_PROVIDER="pgvector"
```

MongoDB remains active for project, asset, and chunk metadata.

---

## Start services

```bash
sudo service docker start

docker compose --env-file .env -f docker/docker-compose.yml up -d
```

Check containers:

```bash
docker compose --env-file .env -f docker/docker-compose.yml ps
```

PostgreSQL must be healthy:

```text
ragforge-postgres   Up ... (healthy)
```

You can also check PostgreSQL readiness directly:

```bash
docker exec -it ragforge-postgres pg_isready -U ragforge -d ragforge
```

Expected:

```text
/var/run/postgresql:5432 - accepting connections
```

---

## Required environment values

For local WSL/host execution, the application connects to PostgreSQL through the mapped host port:

```env
POSTGRES_USER="ragforge"
POSTGRES_PASSWORD="ragforge_password_change_me"
POSTGRES_HOST="localhost"
POSTGRES_PORT=5433
POSTGRES_DB="ragforge"
```

For PgVector as the active vector backend:

```env
VECTOR_DB_PROVIDER="pgvector"
VECTOR_DB_COLLECTION_NAME="ragforge_chunks"
VECTOR_DB_VECTOR_SIZE=1536
VECTOR_DB_DISTANCE="cosine"
```

For real OpenAI embedding validation:

```env
EMBEDDING_PROVIDER="openai_compatible"
EMBEDDING_MODEL="text-embedding-3-small"
EMBEDDING_VECTOR_SIZE=1536
EMBEDDING_OPENAI_API_KEY="YOUR_OPENAI_KEY"
EMBEDDING_OPENAI_BASE_URL="https://api.openai.com/v1"
```

For real grounded answer generation:

```env
LLM_PROVIDER="openai_compatible"
LLM_DEFAULT_MODEL="gpt-4o-mini"
OPENAI_API_KEY="YOUR_OPENAI_KEY"
OPENAI_BASE_URL="https://api.openai.com/v1"
```

Never commit `.env`.

---

## Run migrations

```bash
alembic -c alembic.ini upgrade head
alembic -c alembic.ini current
```

Expected current revision:

```text
20260606_0002 (head)
```

Branch 21 uses the Alembic-managed `vector_records` table.

---

## Validate PostgreSQL and PgVector

Run the Branch 21 validation script:

```bash
python scripts/validation/validate_branch_21_pgvector_provider.py
```

Expected output:

```text
PostgreSQL ping succeeded.
PgVector extension exists.
vector_records table exists.
Configured PgVector index exists.
PgVector insert_many succeeded.
PgVector search_by_vector succeeded.
Branch 21 PgVector provider validation passed.
```

---

## Compile

```bash
python -m compileall src/ragforge migrations scripts/validation tests
```

---

## Run tests

Run Branch 21 tests:

```bash
pytest tests/branch_21_pgvector -q
```

Expected:

```text
46 passed
```

Run the full test suite:

```bash
pytest -q
```

Expected at the time of Branch 21 validation:

```text
93 passed
```

---

## Real PgVector RAG validation

Start the API without reload when Docker data directories are inside the repository:

```bash
uvicorn src.ragforge.main:app --host 127.0.0.1 --port 8000
```

Health check:

```bash
curl -s http://127.0.0.1:8000/api/v1/health/ | python -m json.tool
```

Set variables:

```bash
BASE="http://127.0.0.1:8000/api/v1"
PROJECT_ID="fastapi"
```

The real validation flow is:

```text
Upload document
  ↓
Process into MongoDB chunks
  ↓
Index chunks into PostgreSQL/PgVector
  ↓
Semantic search from PgVector
  ↓
Grounded answer with sources
```

### Indexing

```bash
curl -s -X POST "$BASE/indexing/$PROJECT_ID" \
  -H "Content-Type: application/json" \
  -d '{"do_reset":true}' \
  | python -m json.tool
```

Expected key fields:

```json
{
  "signal": "indexing_success",
  "collection_name": "ragforge_chunks",
  "embedding_model": "text-embedding-3-small",
  "indexed_chunks": 1
}
```

### Semantic search

```bash
curl -s -X POST "$BASE/search/$PROJECT_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "PostgreSQL pgvector extension OpenAI embeddings",
    "limit": 5,
    "include_text": true,
    "include_metadata": true
  }' \
  | python -m json.tool
```

Expected key fields:

```json
{
  "signal": "semantic_search_success",
  "embedding_model": "text-embedding-3-small",
  "total_results": 1
}
```

Result metadata should include:

```json
{
  "embedding_provider": "openai_compatible",
  "embedding_model": "text-embedding-3-small"
}
```

### Grounded answer

```bash
curl -s -X POST "$BASE/answers/$PROJECT_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the goal of RAGForge?",
    "limit": 5
  }' \
  | python -m json.tool
```

Expected key fields:

```json
{
  "signal": "rag_answer_success",
  "llm_model": "gpt-4o-mini",
  "retrieval_count": 3
}
```

The answer should be grounded in retrieved evidence and include citation references such as:

```text
[Source 1]
[Sources 1, 2, 3]
```

---

## Verify vector records

```bash
docker exec -it ragforge-postgres psql -U ragforge -d ragforge -c "
select collection_name, embedding_model, count(*)
from vector_records
group by collection_name, embedding_model;
"
```

Expected example:

```text
 collection_name |    embedding_model       | count
-----------------+--------------------------+-------
 ragforge_chunks | text-embedding-3-small   |     1
```

---

## Switching between PgVector and Qdrant

Use PgVector:

```env
VECTOR_DB_PROVIDER="pgvector"
```

Use Qdrant:

```env
VECTOR_DB_PROVIDER="qdrant"
```

After changing the provider:

```bash
pkill -f "uvicorn src.ragforge.main:app" || true
uvicorn src.ragforge.main:app --host 127.0.0.1 --port 8000
```

Then re-index:

```bash
curl -s -X POST "$BASE/indexing/$PROJECT_ID" \
  -H "Content-Type: application/json" \
  -d '{"do_reset":true}' \
  | python -m json.tool
```

MongoDB remains active in both modes. Only the vector backend changes.

---

## Design rules

- MongoDB remains the active ingestion metadata store for project, asset, and chunk metadata.
- PostgreSQL/PgVector stores vector records through an Alembic-managed `vector_records` table.
- Branch 21 does not create dynamic project-specific vector tables.
- PgVector and Qdrant must both respect the same async `BaseVectorDBProvider` contract.
- `VectorDBService` must stay provider-neutral.
- Provider-specific details stay inside provider implementations and factories.
- `EMBEDDING_VECTOR_SIZE` is the source of truth for vector dimensions.
- `VECTOR_DB_VECTOR_SIZE`, `QDRANT_VECTOR_SIZE`, and `PGVECTOR_VECTOR_SIZE` are optional equality guards only.
- OpenAI `text-embedding-3-small` uses 1536 dimensions in the validated setup.
- Services must not hardcode provider-specific values.
- `.env` must not be committed.
- Docker data directories must stay ignored by Git.
- Uvicorn reload should not watch Docker volume directories.

---

## Branch 21 validation summary

Branch 21 confirms:

```text
PostgreSQL container is healthy.
PgVector extension is available.
Alembic reaches revision 20260606_0002.
vector_records table exists.
Configured PgVector index exists.
PgVector insert_many works.
PgVector search_by_vector works.
Qdrant provider remains compatible with the async provider contract.
Branch 21 test suite passes.
Full test suite passes.
Real OpenAI + PgVector + MongoDB + GPT-4o-mini Postman validation succeeds.
```

The validated real runtime path is:

```text
Postman
  ↓
FastAPI
  ↓
MongoDB metadata / chunks
  ↓
OpenAI text-embedding-3-small
  ↓
PostgreSQL + pgvector
  ↓
Semantic Search
  ↓
Retrieval Postprocessor
  ↓
GPT-4o-mini
  ↓
Citation Validator
  ↓
Grounded Answer with Sources
```
