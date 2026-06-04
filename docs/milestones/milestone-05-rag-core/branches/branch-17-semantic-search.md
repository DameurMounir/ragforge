# Branch 17 — Semantic Search

## Milestone

Milestone 5 — RAG Core: LLM, Vector Store & Retrieval

## Branch

`feature/17-semantic-search`

## Goal

Add the semantic search layer of RAGForge.

Branch 17 converts a user query into an embedding, searches indexed vectors through the provider-neutral vector DB layer, and returns ranked evidence chunks.

The branch implements this flow:

```text
User query
  → EmbeddingProviderFactory
  → Query embedding
  → VectorDBService
  → Vector DB Provider
  → Ranked evidence chunks
```

## Scope

Branch 17 is retrieval-only.

It returns evidence chunks, scores, and source metadata.

It does not generate final answers.

## Why this branch matters

Branch 16 made RAGForge capable of indexing chunks into Qdrant.

Branch 17 makes those indexed chunks searchable.

Branch 18 will reuse Branch 17 to generate grounded answers with sources.

The milestone flow is:

```text
Branch 16 → Indexing
Branch 17 → Semantic Search
Branch 18 → Augmented Answers with Sources
```

## Architecture

```text
routes/search.py
  → SemanticSearchService
  → ProjectStore
  → EmbeddingProviderFactory
  → EmbeddingProvider
  → VectorDBService
  → VectorDBProviderFactory
  → Vector DB Provider
```

## Design rules

Branch 17 follows the RAGForge no-hardcode rule:

```text
.env
  → core/config.py
  → settings
  → service/factory
  → provider
```

Generic services and routes must not use provider-specific configuration names such as `QDRANT_*`.

Provider-specific details stay inside provider factories and provider implementations.

## Added files

```text
src/ragforge/schemas/search.py
src/ragforge/services/semantic_search_service.py
src/ragforge/routes/search.py

scripts/validation/validate_branch_17_semantic_search.py

tests/test_search_schemas.py
tests/test_semantic_search_service.py
```

## Updated files

```text
.env.example
src/ragforge/core/config.py
src/ragforge/main.py
src/ragforge/models/enums/response_signals.py
README.md
docs/milestones/milestone-05-rag-core/milestone-05-rag-core.md
```

## API endpoint

```http
POST /api/v1/search/{project_id}
```

## Request example

```json
{
  "query": "indexing pipeline fake embedding Qdrant",
  "limit": 5,
  "asset_id": null,
  "min_score": null,
  "include_text": true,
  "include_metadata": true
}
```

## Response example

```json
{
  "signal": "semantic_search_success",
  "message": "Semantic search completed.",
  "project_id": "project16test",
  "query": "indexing pipeline fake embedding Qdrant",
  "collection_name": "ragforge_chunks",
  "embedding_model": "fake-embedding-model",
  "total_results": 1,
  "results": [
    {
      "rank": 1,
      "score": 0.91,
      "record_id": "chunk-vector-id",
      "chunk_id": "chunk-id",
      "asset_id": "asset-id",
      "project_id": "mongo-project-object-id",
      "chunk_order": 1,
      "text": "RAGForge Branch 16 validates the indexing pipeline...",
      "metadata": {
        "source_type": "data_chunk",
        "indexing_strategy": "simple_chunk",
        "embedding_model": "fake-embedding-model"
      }
    }
  ]
}
```

## Configuration

Add to `.env.example` and `src/ragforge/core/config.py`:

```env
SEARCH_DEFAULT_LIMIT=5
SEARCH_MAX_LIMIT=20
# SEARCH_MIN_SCORE=
SEARCH_INCLUDE_TEXT_DEFAULT=true
SEARCH_INCLUDE_METADATA_DEFAULT=true
```

## Response signals

Add to `src/ragforge/models/enums/response_signals.py`:

```python
SEMANTIC_SEARCH_SUCCESS = 'semantic_search_success'
SEMANTIC_SEARCH_FAILED = 'semantic_search_failed'
SEMANTIC_SEARCH_NO_RESULTS = 'semantic_search_no_results'
SEARCH_QUERY_EMPTY = 'search_query_empty'
```

## Validation

Use the indexed project from Branch 16:

```bash
python scripts/validation/validate_branch_17_semantic_search.py
```

Expected:

```text
Branch 17 semantic search validation passed
```

## Tests

```bash
pytest
```

Minimum expected coverage:

```text
search request validation
empty query rejection
invalid min_score rejection
project not found
no search results
successful evidence mapping
include_text/include_metadata flags
```

## Architecture audit

No provider-specific config leakage in services/routes:

```bash
grep -R "QDRANT_" -n src/ragforge/services src/ragforge/routes \
  --exclude-dir="__pycache__"
```

Expected:

```text
no output
```

No hidden settings fallback in providers/services/routes:

```bash
grep -R "getattr(settings" -n src/ragforge/providers src/ragforge/services src/ragforge/routes \
  --exclude-dir="__pycache__"
```

Expected:

```text
no output
```

## Not included

Branch 17 does not include:

- answer generation
- prompt building
- LLM calls
- citations formatting
- reranking
- hybrid search
- late chunking implementation
- chat memory
- agents

## Next branch

Branch 18 — Augmented Answers with Sources

Branch 18 will consume the evidence returned by Branch 17 and generate grounded answers through the LLM layer.
