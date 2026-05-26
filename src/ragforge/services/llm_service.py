from src.ragforge.providers.llm.factory import LLMProviderFactory
from src.ragforge.providers.llm.schemas import (
    LLMGenerationRequest,
    LLMGenerationResponse,
)


class LLMService:
    """
    Service layer for LLM generation.

    It keeps routes thin and hides provider creation behind the factory.
    """

    def __init__(self, settings: object):
        self.settings = settings

    async def generate(
        self,
        request: LLMGenerationRequest,
    ) -> LLMGenerationResponse:
        provider = LLMProviderFactory.create_provider(
            settings=self.settings,
            provider=request.provider,
        )

        return await provider.generate(request=request)