# Branch 18 API — Grounded Answer Endpoint

## Endpoint

```http
POST /api/v1/answers/{project_id}
```

## Purpose

Generate a grounded answer from indexed project evidence.

This endpoint reuses Branch 17 semantic search, builds source-numbered context, calls `LLMService`, and returns a structured answer with sources.

## Request body

```json
{
  "question": "What is RAGForge?",
  "limit": 5,
  "asset_id": null,
  "min_score": null,
  "include_sources": true,
  "include_evidence": true,
  "include_debug_prompt": false
}
```

## Fields

| Field | Type | Required | Description |
|---|---:|---:|---|
| `question` | string | yes | User question to answer from indexed evidence. |
| `limit` | integer/null | no | Number of evidence chunks to retrieve. Defaults to `RAG_ANSWER_DEFAULT_LIMIT`. |
| `asset_id` | string/null | no | Optional MongoDB asset id filter. |
| `min_score` | float/null | no | Optional score threshold between 0 and 1. |
| `include_sources` | boolean/null | no | Return source metadata. Defaults to config. |
| `include_evidence` | boolean/null | no | Return evidence text. Defaults to config. |
| `include_debug_prompt` | boolean/null | no | Return the final prompt. Defaults to false. |

## Success response

```json
{
  "signal": "rag_answer_success",
  "message": "Answer generated from retrieved evidence.",
  "project_id": "project18test",
  "question": "What is RAGForge?",
  "answer": "...",
  "sources": [],
  "evidence": [],
  "llm_model": "fake-ragforge-model",
  "retrieval_count": 1,
  "debug_prompt": null
}
```

## No-context response

```json
{
  "signal": "rag_answer_no_context",
  "message": "No relevant indexed evidence was found.",
  "project_id": "project18test",
  "question": "Unknown question?",
  "answer": "I cannot generate a grounded answer because no relevant indexed evidence was found for this project.",
  "sources": [],
  "evidence": [],
  "llm_model": null,
  "retrieval_count": 0,
  "debug_prompt": null
}
```

## Manual curl test

```bash
curl.exe -X POST "http://127.0.0.1:8000/api/v1/answers/project18test" ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"What is RAGForge?\",\"limit\":5,\"include_sources\":true,\"include_evidence\":true,\"include_debug_prompt\":false}"
```
