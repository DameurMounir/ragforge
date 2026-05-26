import asyncio
from types import SimpleNamespace

from src.ragforge.providers.llm.schemas import LLMGenerationRequest
from src.ragforge.services.llm_service import LLMService


def test_llm_service_generates_fake_response():
    settings = SimpleNamespace(
        LLM_PROVIDER='fake',
        LLM_DEFAULT_MODEL='fake-ragforge-model',
    )

    service = LLMService(settings=settings)

    response = asyncio.run(
        service.generate(
            LLMGenerationRequest(
                prompt='What is RAGForge?',
                system_prompt='You are a helpful AI architect.',
            )
        )
    )

    assert response.signal == 'llm_generation_success'
    assert response.provider == 'fake'
    assert response.model == 'fake-ragforge-model'
    assert 'Fake RAGForge response' in response.content
    assert response.metadata['external_call'] is False