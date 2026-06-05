# Branch 19 — RAG Core Stabilization and Local LLM Readiness

## Milestone

Milestone 5 — RAG Core: LLM, Vector Store & Retrieval

## Git branch

```text
feature/19-rag-core-stabilization-local-llm-readiness
```

## Goal

Stabilize the completed RAG Core v1 after Branch 18.

Branch 18 proved that RAGForge can generate grounded answers with sources. Branch 19 makes the core cleaner and safer by improving retrieval quality, controlling noisy evidence, validating citations, documenting real OpenAI usage, and preparing local OpenAI-compatible LLM configuration.

This branch closes Milestone 5.

## Why this branch exists

Postman validation after Branch 18 showed that the core pipeline works with real OpenAI embeddings, real OpenAI-compatible LLM generation, MongoDB metadata, Qdrant vector retrieval, source objects, and evidence text.

The same validation also exposed normal RAG Core v1 issues:

- weak-score chunks may appear in lower-ranked sources,
- a project may contain multiple PDFs with overlapping words,
- evidence should be grouped and cleaned before the prompt,
- citation numbers must never be invented by the LLM,
- local LLM compatibility should be documented without replacing the stable OpenAI path.

Branch 19 fixes those stability issues without introducing agents, workers, authentication, observability dashboards, or production deployment.

## Senior architecture direction

RAGForge must remain a modular knowledge engine, not a monolithic controller.

The Branch 19 flow is:

```text
Answers Route
  ↓
RAGAnswerService
  ↓
SemanticSearchService
  ↓
RetrievalPostprocessor
  ↓
RAGContextBuilder
  ↓
RAG Prompt Builder
  ↓
LLMService
  ↓
CitationValidator
  ↓
Answer + Sources + Evidence + Diagnostics
```

The service boundaries remain strict:

- `SemanticSearchService` retrieves candidate chunks.
- `RetrievalPostprocessor` cleans and groups candidate chunks.
- `RAGContextBuilder` builds source-numbered context.
- `rag_answer_prompt.py` controls answer instructions.
- `LLMService` calls the configured LLM provider.
- `CitationValidator` validates source numbers after generation.

## Main changes

### New files

```text
src/ragforge/services/retrieval_postprocessor.py
src/ragforge/services/citation_validator.py
scripts/validation/validate_branch_19_rag_core_stability.py
tests/test_retrieval_postprocessor.py
tests/test_citation_validator.py
tests/test_rag_answer_service_stability.py
```

### Updated files

```text
src/ragforge/services/rag_answer_service.py
src/ragforge/services/rag_context_builder.py
src/ragforge/prompts/rag_answer_prompt.py
src/ragforge/schemas/answers.py
src/ragforge/core/config.py
.env.example
docs/api/endpoints.md
README.md
docs/milestones/milestone-05-rag-core/milestone-05-rag-core.md
```

## Retrieval post-processing policy

Branch 19 retrieves more candidates than the final answer needs, then cleans them.

Example:

```text
Retrieve 30 candidate chunks
  ↓
Remove empty text
  ↓
Remove weak scores below RAG_RETRIEVAL_MIN_SCORE
  ↓
Remove duplicate chunks
  ↓
Detect dominant asset when one PDF clearly wins
  ↓
Limit max chunks per PDF/asset
  ↓
Keep final 5 sources
```

This keeps the correct chunk-level retrieval behavior while reducing noisy lower-ranked sources.

## Important design nuance

RAGForge should not manually choose one PDF before retrieval.

Correct design:

```text
Project-wide chunk-level vector search
+
Document-aware aggregation after retrieval
```

This allows a project to contain many PDFs. The user asks naturally; RAGForge searches all project chunks, finds the relevant chunks, then identifies the source PDFs using `asset_id`, `source`, `page`, and chunk metadata.

## Configuration added

```env
SEARCH_MAX_LIMIT=50

RAG_RETRIEVAL_CANDIDATE_LIMIT=30
RAG_RETRIEVAL_MIN_SCORE=0.25
RAG_MAX_CHUNKS_PER_ASSET=3
RAG_ENABLE_SOURCE_DEDUP=true
RAG_ENABLE_DOMINANT_ASSET=true
RAG_DOMINANT_ASSET_SCORE_GAP=0.08
RAG_DOMINANT_ASSET_MIN_CHUNKS=2
RAG_ENABLE_CITATION_VALIDATION=true
```

## Real OpenAI production-oriented validation

For real validation, `.env` should use:

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
```

The real key must never be committed.

Fake providers may still be used for fast unit tests and CI, but the Branch 19 manual validation should prefer the real OpenAI path.

## Local LLM readiness

Local LLM support is documented through the existing OpenAI-compatible provider path.

Example local-compatible configuration:

```env
LLM_PROVIDER="openai_compatible"
OPENAI_BASE_URL="http://localhost:11434/v1"
LLM_DEFAULT_MODEL="llama3.1"
```

This branch does not make local LLM mandatory. OpenAI remains the stable validated path.

## Definition of done

Branch 19 is complete when:

1. Unit tests pass.
2. Compile checks pass.
3. Branch 18 real OpenAI flow still works.
4. Retrieval post-processing removes weak chunks.
5. Duplicate sources are reduced.
6. Dominant asset selection works when one PDF clearly wins.
7. Cross-document evidence is preserved when no document clearly dominates.
8. Citation validator detects and sanitizes impossible citations.
9. Answer endpoint returns retrieval diagnostics.
10. Answer endpoint returns citation validation metadata.
11. Real OpenAI validation script passes.
12. README, endpoint docs, and milestone docs are updated.
13. `.env` remains untracked and never committed.

## Validation commands

```bash
python -m compileall src/ragforge
pytest
python scripts/validation/validate_branch_19_rag_core_stability.py
```

For real OpenAI validation:

```bash
export RAGFORGE_EXPECT_REAL_OPENAI=true
export RAGFORGE_VALIDATION_PROJECT_ID=project_postman_reliability
python scripts/validation/validate_branch_19_rag_core_stability.py
```

## Out of scope

Branch 19 does not include:

- agents,
- agent memory,
- Celery workers,
- Redis,
- PostgreSQL/PgVector migration,
- JWT/RBAC,
- dashboard observability,
- RAG evaluation framework,
- streaming answers,
- reranker model integration.

These belong to later milestones.

## Final status sentence

After Branch 19, RAGForge has a stable RAG Core v1: project-based ingestion, MongoDB metadata, OpenAI embeddings, Qdrant vector retrieval, grounded answers with sources, retrieval quality controls, citation validation, and local LLM readiness.
