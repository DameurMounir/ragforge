from src.ragforge.providers.llm.base import BaseLLMProvider
from src.ragforge.providers.llm.enums import LLMProvider
from src.ragforge.providers.llm.exceptions import LLMConfigurationError
from src.ragforge.providers.llm.implementations.fake_provider import (
    FakeLLMProvider,
)
from src.ragforge.providers.llm.implementations.openai_compatible_provider import (
    OpenAICompatibleLLMProvider,
)


class LLMProviderFactory:
    """
    Factory responsible for creating LLM providers from settings.

    Services should not directly instantiate provider classes.
    """

    @staticmethod
    def create_provider(
        settings: object,
        provider: str | LLMProvider | None = None,
    ) -> BaseLLMProvider:
        provider_value = provider or getattr(settings, 'LLM_PROVIDER', 'fake')

        try:
            selected_provider = (
                provider_value
                if isinstance(provider_value, LLMProvider)
                else LLMProvider(str(provider_value))
            )
        except ValueError as error:
            raise LLMConfigurationError(
                f'Unsupported LLM provider: {provider_value}'
            ) from error

        if selected_provider == LLMProvider.FAKE:
            return FakeLLMProvider(
                model=getattr(
                    settings,
                    'LLM_DEFAULT_MODEL',
                    'fake-ragforge-model',
                )
            )

        if selected_provider == LLMProvider.OPENAI_COMPATIBLE:
            return OpenAICompatibleLLMProvider(
                api_key=getattr(settings, 'OPENAI_API_KEY', None),
                base_url=getattr(settings, 'OPENAI_BASE_URL', None),
                model=getattr(settings, 'LLM_DEFAULT_MODEL', None),
                temperature=getattr(settings, 'LLM_TEMPERATURE', 0.2),
                max_output_tokens=getattr(
                    settings,
                    'LLM_MAX_OUTPUT_TOKENS',
                    512,
                ),
                timeout_seconds=getattr(
                    settings,
                    'LLM_TIMEOUT_SECONDS',
                    60,
                ),
            )

        raise LLMConfigurationError(
            f'Unsupported LLM provider: {selected_provider}'
        )