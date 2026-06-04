# Branch 18 — Augmented Answers with Sources

Git branch:

```text
feature/18-augmented-answers-with-sources
```

Milestone:

```text
Milestone 5 — RAG Core: LLM, Vector Store & Retrieval
```

## Goal

Generate grounded answers from retrieved semantic evidence and return structured sources.

## Why this branch exists

Branch 17 returns ranked evidence chunks.

Branch 18 completes the first functional RAG loop by using those chunks to build a controlled context, generate a grounded answer, and return the answer with source metadata.

## Senior architecture decision

Branch 18 must not introduce a large `NLPController` that owns indexing, search, prompting, and answer generation.

RAGForge keeps the professional modular design:

```text
Route
  ↓
Use Case Service
  ↓
Specialized Services
  ↓
Provider Interfaces
  ↓
Provider Implementations
```

Branch 18 therefore adds a focused answer layer:

```text
POST /api/v1/answers/{project_id}
  ↓
RAGAnswerService
  ↓
SemanticSearchService
  ↓
RAGContextBuilder
  ↓
RAG Prompt Builder
  ↓
LLMService
  ↓
Answer + Sources + Evidence
```

## Main components

- `src/ragforge/schemas/answers.py`
- `src/ragforge/services/rag_answer_service.py`
- `src/ragforge/services/rag_context_builder.py`
- `src/ragforge/prompts/rag_answer_prompt.py`
- `src/ragforge/routes/answers.py`
- `scripts/validation/validate_branch_18_answers.py`
- `tests/test_answer_schemas.py`
- `tests/test_rag_context_builder.py`
- `tests/test_rag_answer_service.py`

## Design decisions

- Branch 18 reuses Branch 17 semantic search.
- The answer service does not know Qdrant internals.
- The answer service does not call embedding providers directly.
- The answer service does not call OpenAI/Ollama/LocalAI directly.
- Prompt construction is isolated from answer orchestration.
- Sources are first-class response objects.
- Evidence can be returned for inspection and debugging.
- Debug prompt is hidden by default.
- All operational defaults are declared in `core/config.py` and `.env.example`.

## Endpoint

```http
POST /api/v1/answers/{project_id}
```

## Example request

```json
{
  "question": "What does this project say about indexing?",
  "limit": 5,
  "asset_id": null,
  "min_score": null,
  "include_sources": true,
  "include_evidence": true,
  "include_debug_prompt": false
}
```

## Example response

```json
{
  "signal": "rag_answer_success",
  "message": "Answer generated from retrieved evidence.",
  "project_id": "project18test",
  "question": "What does this project say about indexing?",
  "answer": "...",
  "sources": [
    {
      "source_number": 1,
      "rank": 1,
      "score": 0.91,
      "record_id": "record-1",
      "chunk_id": "chunk-1",
      "asset_id": "asset-1",
      "project_id": "mongo-project-id",
      "chunk_order": 1,
      "metadata": {}
    }
  ],
  "evidence": [
    {
      "source_number": 1,
      "text": "...",
      "score": 0.91,
      "chunk_id": "chunk-1",
      "asset_id": "asset-1",
      "chunk_order": 1,
      "metadata": {}
    }
  ],
  "llm_model": "fake-ragforge-model",
  "retrieval_count": 1,
  "debug_prompt": null
}
```

## Out of scope

Branch 18 does not include:

- agents,
- chat memory,
- hybrid search,
- reranking,
- streaming responses,
- background workers,
- observability dashboard,
- production deployment.

## Validation commands

```bash
python -m py_compile \
  src/ragforge/schemas/answers.py \
  src/ragforge/services/rag_context_builder.py \
  src/ragforge/prompts/rag_answer_prompt.py \
  src/ragforge/services/rag_answer_service.py \
  src/ragforge/routes/answers.py

python -m compileall src/ragforge
pytest tests/test_answer_schemas.py -v
pytest tests/test_rag_context_builder.py -v
pytest tests/test_rag_answer_service.py -v
pytest
python scripts/validation/validate_branch_18_answers.py
```

## Definition of done

- `/api/v1/answers/{project_id}` exists.
- The route is thin.
- `RAGAnswerService` orchestrates the answer flow.
- `SemanticSearchService` is reused.
- `RAGContextBuilder` creates source-numbered context.
- Prompt logic is isolated.
- LLM generation goes through `LLMService`.
- Response returns answer, sources, evidence, model, and retrieval count.
- Debug prompt is hidden unless requested.
- Unit tests pass.
- Validation script passes.
- README and Milestone 5 docs are updated.
