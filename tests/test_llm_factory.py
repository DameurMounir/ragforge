import pytest
from types import SimpleNamespace

from src.ragforge.providers.llm.exceptions import LLMConfigurationError
from src.ragforge.providers.llm.factory import LLMProviderFactory
from src.ragforge.providers.llm.implementations.fake_provider import (
    FakeLLMProvider,
)


def test_llm_factory_creates_fake_provider():
    settings = SimpleNamespace(
        LLM_PROVIDER='fake',
        LLM_DEFAULT_MODEL='fake-ragforge-model',
    )

    provider = LLMProviderFactory.create_provider(settings=settings)

    assert isinstance(provider, FakeLLMProvider)


def test_llm_factory_rejects_unknown_provider():
    settings = SimpleNamespace(
        LLM_PROVIDER='unknown_provider',
        LLM_DEFAULT_MODEL='fake-ragforge-model',
    )

    with pytest.raises(LLMConfigurationError):
        LLMProviderFactory.create_provider(settings=settings)