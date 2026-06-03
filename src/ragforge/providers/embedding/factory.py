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
    """

    @staticmethod
    def create_provider(settings: object) -> BaseEmbeddingProvider:
        provider_value = getattr(settings, 'EMBEDDING_PROVIDER', 'fake')

        try:
            selected_provider = EmbeddingProvider(str(provider_value))
        except ValueError as error:
            raise EmbeddingConfigurationError(
                f'Unsupported embedding provider: {provider_value}'
            ) from error

        dimensions = getattr(settings, 'EMBEDDING_VECTOR_SIZE', 1536)
        model = getattr(settings, 'EMBEDDING_MODEL', 'text-embedding-3-small')

        if selected_provider == EmbeddingProvider.FAKE:
            return FakeEmbeddingProvider(
                model='fake-embedding-model',
                dimensions=dimensions,
            )

        if selected_provider == EmbeddingProvider.OPENAI_COMPATIBLE:
            api_key = (
                getattr(settings, 'EMBEDDING_OPENAI_API_KEY', None)
                or getattr(settings, 'OPENAI_API_KEY', None)
            )

            base_url = (
                getattr(settings, 'EMBEDDING_OPENAI_BASE_URL', None)
                or getattr(settings, 'OPENAI_BASE_URL', None)
            )

            if base_url == '':
                base_url = None

            return OpenAICompatibleEmbeddingProvider(
                api_key=api_key,
                base_url=base_url,
                model=model,
                dimensions=dimensions,
            )

        raise EmbeddingConfigurationError(
            f'Unsupported embedding provider: {selected_provider}'
        )
