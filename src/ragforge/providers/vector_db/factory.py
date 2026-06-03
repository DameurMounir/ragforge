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

    Provider-specific configuration is allowed here because this is the
    provider selection boundary.

    Runtime defaults must come from core/config.py, not from this factory.
    """

    @staticmethod
    def create_provider(settings: object) -> BaseVectorDBProvider:
        provider_value = settings.VECTOR_DB_PROVIDER

        try:
            selected_provider = VectorDBProvider(str(provider_value))
        except ValueError as error:
            raise VectorDBConfigurationError(
                f'Unsupported vector DB provider: {provider_value}'
            ) from error

        if selected_provider == VectorDBProvider.QDRANT:
            return QdrantProvider(
                mode=settings.QDRANT_MODE,
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
                local_path=settings.QDRANT_LOCAL_PATH,
                prefer_grpc=settings.QDRANT_PREFER_GRPC,
            )

        raise VectorDBConfigurationError(
            f'Unsupported vector DB provider: {selected_provider}'
        )
