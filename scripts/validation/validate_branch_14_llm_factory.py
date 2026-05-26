import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from src.ragforge.providers.llm.factory import LLMProviderFactory
from src.ragforge.providers.llm.schemas import LLMGenerationRequest
from src.ragforge.services.llm_service import LLMService


async def main():
    settings = SimpleNamespace(
        LLM_PROVIDER='fake',
        LLM_DEFAULT_MODEL='fake-ragforge-model',
        LLM_TEMPERATURE=0.2,
        LLM_MAX_OUTPUT_TOKENS=512,
        LLM_TIMEOUT_SECONDS=60,
        OPENAI_API_KEY=None,
        OPENAI_BASE_URL=None,
    )

    provider = LLMProviderFactory.create_provider(settings=settings)
    service = LLMService(settings=settings)

    response = await service.generate(
        LLMGenerationRequest(
            prompt='Validate Branch 14 LLM Factory.',
            system_prompt='You are a professional RAG backend validator.',
        )
    )

    print('Branch 14 validation started.')
    print(f'Provider class: {provider.__class__.__name__}')
    print(f'Response signal: {response.signal}')
    print(f'Response provider: {response.provider}')
    print(f'Response model: {response.model}')
    print(f'Response content: {response.content}')
    print('Branch 14 validation passed.')


if __name__ == '__main__':
    asyncio.run(main())