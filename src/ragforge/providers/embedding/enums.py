from enum import Enum


class EmbeddingProvider(str, Enum):
    FAKE = 'fake'
    OPENAI_COMPATIBLE = 'openai_compatible'


class IndexingGranularity(str, Enum):
    CHUNK = 'chunk'
    ASSET = 'asset'
    DOCUMENT = 'document'
    SECTION = 'section'


class IndexingStrategy(str, Enum):
    SIMPLE_CHUNK = 'simple_chunk'
    LATE_CHUNKING = 'late_chunking'
    ASSET_SUMMARY = 'asset_summary'
    HIERARCHICAL = 'hierarchical'
