# Branch 14 — LLM Factory Local Development

## Fake Provider Configuration

Use this `.env` configuration for local tests:

```env
LLM_PROVIDER="fake"
LLM_DEFAULT_MODEL="fake-ragforge-model"
LLM_TEMPERATURE=0.2
LLM_MAX_OUTPUT_TOKENS=512
LLM_TIMEOUT_SECONDS=60

OPENAI_API_KEY=""
OPENAI_BASE_URL=""
```

---

## Run Tests

```bash
python -m pytest tests/test_llm_factory.py tests/test_llm_service.py -v
python scripts/validation/validate_branch_14_llm_factory.py
```

---

## Run Server

```bash
uvicorn src.ragforge.main:app --reload --reload-dir src --host 127.0.0.1 --port 8000
```

---

## Test API

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

Expected result:

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
