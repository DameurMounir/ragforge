from src.ragforge.providers.vector_db.base import BaseVectorDBProvider
from src.ragforge.providers.vector_db.enums import VectorDBProvider
from src.ragforge.providers.vector_db.exceptions import (
    VectorDBConfigurationError,
)
from src.ragforge.providers.vector_db.implementations.qdrant_provider import (
    QdrantProvider,
)


class VectorDBProviderFactory:
    """
    Factory responsible for creating vector DB providers from settings.

    Services should not directly instantiate provider classes.
    """

    @staticmethod
    def create_provider(
        settings: object,
        provider: str | VectorDBProvider | None = None,
    ) -> BaseVectorDBProvider:
        provider_value = provider or getattr(
            settings,
            'VECTOR_DB_PROVIDER',
            'qdrant',
        )

        try:
            selected_provider = (
                provider_value
                if isinstance(provider_value, VectorDBProvider)
                else VectorDBProvider(str(provider_value))
            )
        except ValueError as error:
            raise VectorDBConfigurationError(
                f'Unsupported vector DB provider: {provider_value}'
            ) from error

        if selected_provider == VectorDBProvider.QDRANT:
            return QdrantProvider(
                mode=getattr(settings, 'QDRANT_MODE', 'server'),
                url=getattr(settings, 'QDRANT_URL', 'http://localhost:6333'),
                api_key=getattr(settings, 'QDRANT_API_KEY', None),
                local_path=getattr(
                    settings,
                    'QDRANT_LOCAL_PATH',
                    'storage/vector_db/qdrant',
                ),
                prefer_grpc=getattr(settings, 'QDRANT_PREFER_GRPC', False),
            )

        raise VectorDBConfigurationError(
            f'Unsupported vector DB provider: {selected_provider}'
        )