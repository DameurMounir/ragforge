from src.ragforge.providers.llm.base import BaseLLMProvider
from src.ragforge.providers.llm.schemas import (
    LLMGenerationRequest,
    LLMGenerationResponse,
    LLMUsage,
)


class FakeLLMProvider(BaseLLMProvider):
    """
    Deterministic provider used for tests and local validation.

    It never calls an external API.
    """

    def __init__(self, model: str = 'fake-ragforge-model'):
        self.model = model

    async def generate(
        self,
        request: LLMGenerationRequest,
    ) -> LLMGenerationResponse:
        messages = request.to_messages()

        last_user_message = next(
            (
                message.content
                for message in reversed(messages)
                if message.role == 'user'
            ),
            '',
        )

        content = (
            'Fake RAGForge response generated successfully. '
            f'Input preview: {last_user_message[:120]}'
        )

        input_tokens = len(last_user_message.split())
        output_tokens = len(content.split())

        return LLMGenerationResponse(
            provider='fake',
            model=request.model or self.model,
            content=content,
            finish_reason='stop',
            usage=LLMUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
            ),
            metadata={
                'deterministic': True,
                'external_call': False,
            },
        )