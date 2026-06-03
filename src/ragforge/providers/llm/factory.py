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

    Runtime defaults must come from core/config.py, not from this factory.
    Services should not directly instantiate provider classes.
    """

    @staticmethod
    def create_provider(
        settings: object,
        provider: str | LLMProvider | None = None,
    ) -> BaseLLMProvider:
        provider_value = provider or settings.LLM_PROVIDER

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
                model=settings.LLM_DEFAULT_MODEL,
            )

        if selected_provider == LLMProvider.OPENAI_COMPATIBLE:
            base_url = settings.OPENAI_BASE_URL

            if base_url == '':
                base_url = None

            return OpenAICompatibleLLMProvider(
                api_key=settings.OPENAI_API_KEY,
                base_url=base_url,
                model=settings.LLM_DEFAULT_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                max_output_tokens=settings.LLM_MAX_OUTPUT_TOKENS,
                timeout_seconds=settings.LLM_TIMEOUT_SECONDS,
            )

        raise LLMConfigurationError(
            f'Unsupported LLM provider: {selected_provider}'
        )
