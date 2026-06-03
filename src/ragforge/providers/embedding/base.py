from abc import ABC, abstractmethod

from src.ragforge.providers.embedding.schemas import (
    EmbeddingRequest,
    EmbeddingResponse,
)


class BaseEmbeddingProvider(ABC):
    """
    Base interface for all embedding providers.

    Indexing code must depend on this interface, not directly on OpenAI,
    Jina, Hugging Face, Ollama, or any future provider.
    """

    @abstractmethod
    def embed_texts(
        self,
        embedding_request: EmbeddingRequest,
    ) -> EmbeddingResponse:
        raise NotImplementedError
