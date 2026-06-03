from openai import OpenAI

from src.ragforge.providers.embedding.base import BaseEmbeddingProvider
from src.ragforge.providers.embedding.exceptions import (
    EmbeddingConfigurationError,
)
from src.ragforge.providers.embedding.schemas import (
    EmbeddingRequest,
    EmbeddingResponse,
)


class OpenAICompatibleEmbeddingProvider(BaseEmbeddingProvider):
    """
    OpenAI-compatible embedding provider.

    Works with OpenAI and OpenAI-compatible APIs when they support
    the embeddings endpoint.
    """

    def __init__(
        self,
        api_key: str | None,
        model: str,
        dimensions: int,
        base_url: str | None = None,
    ):
        if not api_key:
            raise EmbeddingConfigurationError(
                'OpenAI-compatible embedding provider requires an API key.'
            )

        self.model = model
        self.dimensions = dimensions

        client_kwargs = {'api_key': api_key}

        if base_url:
            client_kwargs['base_url'] = base_url

        self.client = OpenAI(**client_kwargs)

    def embed_texts(
        self,
        embedding_request: EmbeddingRequest,
    ) -> EmbeddingResponse:
        model = embedding_request.model or self.model

        response = self.client.embeddings.create(
            model=model,
            input=embedding_request.texts,
            dimensions=self.dimensions,
        )

        sorted_items = sorted(response.data, key=lambda item: item.index)

        embeddings = [
            item.embedding
            for item in sorted_items
        ]

        usage = {}

        if response.usage is not None:
            usage = response.usage.model_dump()

        return EmbeddingResponse(
            embeddings=embeddings,
            model=model,
            dimensions=len(embeddings[0]) if embeddings else self.dimensions,
            usage=usage,
        )
