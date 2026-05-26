# Branch 14 — LLM Factory

## Branch Identity

| Field | Value |
|---|---|
| Milestone | Milestone 5 — RAG Core: LLM, Vector Store & Retrieval |
| Branch number | 14 |
| Branch name | LLM Factory |
| Git branch | `feature/14-llm-factory` |
| Issue title | Create provider-neutral LLM factory |
| PR title | Create provider-neutral LLM factory |

---

## Objective

Create a provider-neutral LLM Factory for RAGForge.

Branch 14 starts the real RAG Core by adding a clean LLM generation layer.

The goal is to allow RAGForge to generate responses without being locked to one provider such as OpenAI, OpenRouter, Ollama, LM Studio, Gemini-compatible endpoints, or any other OpenAI-compatible backend.

---

## Why this branch exists

RAGForge needs an LLM layer before it can generate augmented answers.

However, the LLM layer must be separated from:

- document upload
- document processing
- MongoDB metadata
- vector database
- embeddings
- semantic search
- agent orchestration

This branch creates the intelligence gateway that future branches will reuse.

---

## Architectural Decision

The teacher reference uses an educational `stores/llm` structure.

RAGForge uses a cleaner professional structure:

```text
src/ragforge/providers/llm/
```

Reason:

```text
MongoDB is a store.
OpenAI-compatible APIs are providers.
```

Therefore, LLM providers should live under a provider layer, not a persistence store layer.

---

## Target Architecture

```text
POST /api/v1/llm/generate
        ↓
routes/llm.py
        ↓
LLMService
        ↓
LLMProviderFactory
        ↓
BaseLLMProvider
        ↓
FakeLLMProvider or OpenAICompatibleLLMProvider
        ↓
LLMGenerationResponse
```

---

## Added Structure

```text
src/ragforge/
├── providers/
│   └── llm/
│       ├── __init__.py
│       ├── enums.py
│       ├── schemas.py
│       ├── exceptions.py
│       ├── base.py
│       ├── factory.py
│       └── implementations/
│           ├── __init__.py
│           ├── fake_provider.py
│           └── openai_compatible_provider.py
│
├── services/
│   └── llm_service.py
│
├── routes/
│   └── llm.py
```

---

## Added Components

### 1. LLMProvider enum

Defines supported LLM providers.

Current providers:

```text
fake
openai_compatible
```

---

### 2. LLM schemas

Provider-neutral schemas:

- `LLMMessage`
- `LLMGenerationRequest`
- `LLMUsage`
- `LLMGenerationResponse`

The request supports both simple prompt mode and message-list mode.

Example:

```json
{
  "prompt": "Explain Branch 14 in one sentence.",
  "system_prompt": "You are a professional AI backend architect.",
  "temperature": 0.2,
  "max_output_tokens": 200
}
```

---

### 3. LLM exceptions

Custom exceptions:

- `LLMError`
- `LLMConfigurationError`
- `LLMProviderError`

These allow routes to return clean API errors instead of crashing.

---

### 4. BaseLLMProvider

Abstract interface that every LLM provider must implement.

Required method:

```python
async def generate(request: LLMGenerationRequest) -> LLMGenerationResponse
```

---

### 5. FakeLLMProvider

Deterministic provider used for:

- local development
- unit tests
- CI
- validation without API cost
- validation without external network

It returns a fake response and marks:

```json
{
  "deterministic": true,
  "external_call": false
}
```

---

### 6. OpenAICompatibleLLMProvider

Provider for OpenAI-compatible chat completions APIs.

It can support:

- OpenAI
- OpenRouter
- Ollama OpenAI-compatible endpoint
- LM Studio
- Together AI
- other compatible gateways

For real OpenAI, keep:

```env
OPENAI_BASE_URL=""
```

For custom compatible gateways, set:

```env
OPENAI_BASE_URL="https://your-compatible-endpoint/v1"
```

---

### 7. LLMProviderFactory

Creates the correct provider from settings.

Service code does not directly instantiate concrete providers.

This keeps the service layer provider-neutral.

---

### 8. LLMService

Service layer responsible for LLM generation.

It receives a generation request, asks the factory for a provider, then returns the provider response.

---

### 9. LLM route

Branch 14 adds:

```text
POST /api/v1/llm/generate
```

This endpoint validates the LLM Factory before vector search and RAG answers exist.

---

## API Endpoint

### POST `/api/v1/llm/generate`

Generate a provider-neutral LLM response.

### Example Request

```json
{
  "provider": "fake",
  "prompt": "Validate Branch 14 API endpoint.",
  "system_prompt": "You are a professional RAGForge validator.",
  "temperature": 0.2,
  "max_output_tokens": 200
}
```

### Example Response

```json
{
  "signal": "llm_generation_success",
  "provider": "fake",
  "model": "fake-ragforge-model",
  "content": "Fake RAGForge response generated successfully. Input preview: Validate Branch 14 API endpoint.",
  "finish_reason": "stop",
  "usage": {
    "input_tokens": 5,
    "output_tokens": 12,
    "total_tokens": 17
  },
  "metadata": {
    "deterministic": true,
    "external_call": false
  }
}
```

---

## Environment Variables

### Local fake provider

```env
LLM_PROVIDER="fake"
LLM_DEFAULT_MODEL="fake-ragforge-model"
LLM_TEMPERATURE=0.2
LLM_MAX_OUTPUT_TOKENS=512
LLM_TIMEOUT_SECONDS=60

OPENAI_API_KEY=""
OPENAI_BASE_URL=""
```

### Real OpenAI provider

```env
LLM_PROVIDER="openai_compatible"
LLM_DEFAULT_MODEL="gpt-4o-mini"
LLM_TEMPERATURE=0.2
LLM_MAX_OUTPUT_TOKENS=512
LLM_TIMEOUT_SECONDS=60

OPENAI_API_KEY="your_real_key_here"
OPENAI_BASE_URL=""
```

### OpenRouter or local compatible gateway

```env
LLM_PROVIDER="openai_compatible"
LLM_DEFAULT_MODEL="your_model_name"
LLM_TEMPERATURE=0.2
LLM_MAX_OUTPUT_TOKENS=512
LLM_TIMEOUT_SECONDS=60

OPENAI_API_KEY="your_key_here"
OPENAI_BASE_URL="https://your-compatible-endpoint/v1"
```

---

## Validation Commands

### Run unit tests

```bash
python -m pytest tests/test_llm_factory.py tests/test_llm_service.py -v
```

### Run all tests

```bash
python -m pytest
```

### Run Branch 14 validation script

```bash
python scripts/validation/validate_branch_14_llm_factory.py
```

### Run FastAPI server

```bash
uvicorn src.ragforge.main:app --reload --reload-dir src --host 127.0.0.1 --port 8000
```

### Test with curl

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/llm/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "fake",
    "prompt": "Validate Branch 14 API endpoint.",
    "system_prompt": "You are a professional RAGForge validator.",
    "temperature": 0.2,
    "max_output_tokens": 200
  }'
```

---

## Validation Result

Branch 14 is validated when the API returns:

```json
{
  "signal": "llm_generation_success",
  "provider": "fake",
  "model": "fake-ragforge-model",
  "metadata": {
    "deterministic": true,
    "external_call": false
  }
}
```

---

## Out of Scope

Branch 14 must not introduce:

- vector database
- embeddings
- chunk indexing
- semantic search
- augmented answers with sources
- agent orchestration
- Celery workers
- observability dashboard
- security/RBAC layer

---

## Definition of Done

Branch 14 is complete when:

1. `feature/14-llm-factory` exists.
2. LLM provider enum is implemented.
3. LLM request and response schemas are implemented.
4. LLM exceptions are implemented.
5. `BaseLLMProvider` exists.
6. `FakeLLMProvider` works without API key.
7. `OpenAICompatibleLLMProvider` exists.
8. `LLMProviderFactory` creates providers from settings.
9. `LLMService` hides provider logic from routes.
10. `/api/v1/llm/generate` works.
11. `.env.example` is updated.
12. `requirements.txt` includes OpenAI SDK.
13. Unit tests pass.
14. Validation script passes.
15. API curl test passes with fake provider.
16. README points to Branch 14.
17. Milestone 5 documentation exists.
18. Branch 14 documentation exists.
19. Pull request is opened with clean scope.

---

## Professional Summary

Branch 14 creates the provider-neutral intelligence gateway of RAGForge.

It is the first real RAG Core branch.

It prepares the system for future grounded answers while keeping embeddings, vector database, retrieval, and agent logic separated into later branches.
