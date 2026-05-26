from abc import ABC, abstractmethod

from src.ragforge.providers.llm.schemas import (
    LLMGenerationRequest,
    LLMGenerationResponse,
)


class BaseLLMProvider(ABC):
    """
    Abstract interface for all LLM providers.

    RAGForge services must depend on this interface, not directly on
    OpenAI, OpenRouter, Ollama, Gemini, Claude, or any concrete provider.
    """

    @abstractmethod
    async def generate(
        self,
        request: LLMGenerationRequest,
    ) -> LLMGenerationResponse:
        raise NotImplementedError