# Branch 19 API Notes — Answer Quality Controls

Branch 19 keeps the same answer endpoint:

```text
POST /api/v1/answers/{project_id}
```

The request remains compatible with Branch 18:

```json
{
  "question": "Does MongoDB replace Qdrant?",
  "limit": 5,
  "asset_id": null,
  "min_score": null,
  "include_sources": true,
  "include_evidence": true,
  "include_debug_prompt": false
}
```

## New behavior

The endpoint now retrieves a larger candidate set, cleans it, then keeps only the strongest final evidence.

The response adds:

```json
{
  "warnings": [],
  "retrieval_diagnostics": {
    "candidate_count": 30,
    "removed_below_min_score": 12,
    "removed_duplicates": 0,
    "removed_by_asset_limit": 3,
    "dominant_asset_applied": true,
    "dominant_asset_id": "...",
    "final_count": 5
  },
  "citation_validation": {
    "valid_source_numbers": [1, 2, 3, 4, 5],
    "cited_source_numbers": [1, 2],
    "invalid_source_numbers": [],
    "was_modified": false
  }
}
```

## Why this matters

A project can contain many PDFs. Retrieval must remain project-wide and chunk-level, but answer context must be document-aware and clean.

Branch 19 improves:

- weak-score filtering,
- duplicate removal,
- max chunks per PDF/asset,
- dominant asset detection,
- invalid citation detection,
- safer no-context responses.

## Recommended production-oriented `.env`

```env
LLM_PROVIDER="openai_compatible"
LLM_DEFAULT_MODEL="gpt-4.1-mini"
OPENAI_API_KEY="your-local-key-only"
OPENAI_BASE_URL=""

EMBEDDING_PROVIDER="openai_compatible"
EMBEDDING_MODEL="text-embedding-3-small"
EMBEDDING_VECTOR_SIZE=1536
EMBEDDING_OPENAI_API_KEY="your-local-key-only"
EMBEDDING_OPENAI_BASE_URL=""

SEARCH_MAX_LIMIT=50
RAG_RETRIEVAL_CANDIDATE_LIMIT=30
RAG_RETRIEVAL_MIN_SCORE=0.25
RAG_MAX_CHUNKS_PER_ASSET=3
RAG_ENABLE_SOURCE_DEDUP=true
RAG_ENABLE_DOMINANT_ASSET=true
RAG_ENABLE_CITATION_VALIDATION=true
```

Never commit the local `.env` file.
