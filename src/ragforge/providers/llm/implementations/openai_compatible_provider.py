from openai import AsyncOpenAI

from src.ragforge.providers.llm.base import BaseLLMProvider
from src.ragforge.providers.llm.exceptions import (
    LLMConfigurationError,
    LLMProviderError,
)
from src.ragforge.providers.llm.schemas import (
    LLMGenerationRequest,
    LLMGenerationResponse,
    LLMUsage,
)


class OpenAICompatibleLLMProvider(BaseLLMProvider):
    """
    OpenAI-compatible chat completions provider.

    This provider can support:
    - OpenAI
    - OpenRouter
    - LM Studio
    - Ollama OpenAI-compatible gateways
    - Together AI
    - Gemini OpenAI-compatible endpoint
    - Claude OpenAI-compatible endpoint

    The key is to configure:
    - API key
    - base_url when needed
    - model name
    """

    def __init__(
        self,
        api_key: str | None,
        model: str | None,
        base_url: str | None = None,
        temperature: float = 0.2,
        max_output_tokens: int = 512,
        timeout_seconds: int = 60,
    ):
        if not api_key:
            raise LLMConfigurationError(
                'OPENAI_API_KEY is required for openai_compatible provider.'
            )

        if not model:
            raise LLMConfigurationError(
                'LLM_DEFAULT_MODEL is required for openai_compatible provider.'
            )

        self.model = model
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens

        client_kwargs = {
            'api_key': api_key,
            'timeout': timeout_seconds,
        }

        if base_url:
            client_kwargs['base_url'] = base_url

        self.client = AsyncOpenAI(**client_kwargs)

    async def generate(
        self,
        request: LLMGenerationRequest,
    ) -> LLMGenerationResponse:
        model = request.model or self.model

        temperature = (
            request.temperature
            if request.temperature is not None
            else self.temperature
        )

        max_output_tokens = (
            request.max_output_tokens
            if request.max_output_tokens is not None
            else self.max_output_tokens
        )

        messages = [
            {
                'role': message.role,
                'content': message.content,
            }
            for message in request.to_messages()
        ]

        try:
            completion = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_output_tokens,
            )
        except Exception as error:
            raise LLMProviderError(
                f'OpenAI-compatible generation failed: {error}'
            ) from error

        if not completion.choices:
            raise LLMProviderError(
                'OpenAI-compatible provider returned no choices.'
            )

        choice = completion.choices[0]
        usage = getattr(completion, 'usage', None)

        return LLMGenerationResponse(
            provider='openai_compatible',
            model=model,
            content=choice.message.content or '',
            finish_reason=choice.finish_reason,
            usage=LLMUsage(
                input_tokens=getattr(usage, 'prompt_tokens', None)
                if usage
                else None,
                output_tokens=getattr(usage, 'completion_tokens', None)
                if usage
                else None,
                total_tokens=getattr(usage, 'total_tokens', None)
                if usage
                else None,
            ),
            metadata={
                'external_call': True,
            },
        )