import hashlib
import math

from src.ragforge.providers.embedding.base import BaseEmbeddingProvider
from src.ragforge.providers.embedding.schemas import (
    EmbeddingRequest,
    EmbeddingResponse,
)


class FakeEmbeddingProvider(BaseEmbeddingProvider):
    """
    Deterministic fake embedding provider for tests and local validation.

    It does not call external APIs.
    It creates stable pseudo-vectors from text hashes.

    Model name and dimensions are injected from settings through the factory.
    """

    def __init__(
        self,
        model: str,
        dimensions: int,
    ):
        self.model = model
        self.dimensions = dimensions

    def embed_texts(
        self,
        embedding_request: EmbeddingRequest,
    ) -> EmbeddingResponse:
        embeddings = [
            self._text_to_vector(text=text)
            for text in embedding_request.texts
        ]

        return EmbeddingResponse(
            embeddings=embeddings,
            model=self.model,
            dimensions=self.dimensions,
            usage={
                'provider': 'fake',
                'texts': len(embedding_request.texts),
            },
        )

    def _text_to_vector(self, text: str) -> list[float]:
        values: list[float] = []
        seed = text or 'empty-text'

        for index in range(self.dimensions):
            raw = f'{seed}:{index}'.encode('utf-8')
            digest = hashlib.sha256(raw).digest()
            integer = int.from_bytes(digest[:4], byteorder='big')
            value = (integer / 2**32) * 2 - 1
            values.append(value)

        norm = math.sqrt(sum(value * value for value in values))

        if norm == 0:
            return values

        return [value / norm for value in values]
