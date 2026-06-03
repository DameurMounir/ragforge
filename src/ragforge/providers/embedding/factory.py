from src.ragforge.providers.embedding.base import BaseEmbeddingProvider
from src.ragforge.providers.embedding.enums import EmbeddingProvider
from src.ragforge.providers.embedding.exceptions import (
    EmbeddingConfigurationError,
)
from src.ragforge.providers.embedding.implementations.fake_embedding_provider import (
    FakeEmbeddingProvider,
)
from src.ragforge.providers.embedding.implementations.openai_compatible_embedding_provider import (
    OpenAICompatibleEmbeddingProvider,
)


class EmbeddingProviderFactory:
    """
    Factory responsible for creating embedding providers from settings.

    Runtime defaults must come from core/config.py, not from this factory.
    """

    @staticmethod
    def create_provider(settings: object) -> BaseEmbeddingProvider:
        provider_value = settings.EMBEDDING_PROVIDER

        try:
            selected_provider = EmbeddingProvider(str(provider_value))
        except ValueError as error:
            raise EmbeddingConfigurationError(
                f'Unsupported embedding provider: {provider_value}'
            ) from error

        if selected_provider == EmbeddingProvider.FAKE:
            return FakeEmbeddingProvider(
                model=settings.FAKE_EMBEDDING_MODEL,
                dimensions=settings.EMBEDDING_VECTOR_SIZE,
            )

        if selected_provider == EmbeddingProvider.OPENAI_COMPATIBLE:
            api_key = (
                settings.EMBEDDING_OPENAI_API_KEY
                or settings.OPENAI_API_KEY
            )

            base_url = (
                settings.EMBEDDING_OPENAI_BASE_URL
                or settings.OPENAI_BASE_URL
            )

            if base_url == '':
                base_url = None

            return OpenAICompatibleEmbeddingProvider(
                api_key=api_key,
                base_url=base_url,
                model=settings.EMBEDDING_MODEL,
                dimensions=settings.EMBEDDING_VECTOR_SIZE,
            )

        raise EmbeddingConfigurationError(
            f'Unsupported embedding provider: {selected_provider}'
        )
