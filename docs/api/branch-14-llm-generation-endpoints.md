# API Documentation — Branch 14 LLM Generation

## LLM Generation

### POST `/api/v1/llm/generate`

Generates a response through the provider-neutral LLM Factory.

This endpoint was introduced in Branch 14 to validate the LLM abstraction before vector search, embeddings, semantic search, and grounded answers are introduced.

---

## Request Body

```json
{
  "provider": "fake",
  "prompt": "Validate Branch 14 API endpoint.",
  "system_prompt": "You are a professional RAGForge validator.",
  "temperature": 0.2,
  "max_output_tokens": 200
}
```

---

## Successful Response

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

## Error Responses

### Invalid provider configuration

```json
{
  "signal": "llm_configuration_error",
  "message": "Unsupported LLM provider: unknown_provider"
}
```

### External provider failure

```json
{
  "signal": "llm_provider_error",
  "message": "OpenAI-compatible generation failed: Connection error."
}
```

---

## Notes

- Default local test provider is `fake`.
- `fake` requires no API key and makes no external call.
- `openai_compatible` requires `OPENAI_API_KEY`.
- For real OpenAI, keep `OPENAI_BASE_URL` empty.
- For OpenRouter, Ollama, LM Studio, or another OpenAI-compatible gateway, set `OPENAI_BASE_URL`.
- This endpoint does not perform retrieval.
- This endpoint does not use embeddings.
- This endpoint does not return sources.
