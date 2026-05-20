from enum import Enum


class AssetType(str, Enum):
    """
    Supported asset types in the RAGForge ingestion pipeline.

    An asset is any knowledge source that can later be processed into chunks.
    """

    FILE = 'file'
    URL = 'url'
    IMAGE = 'image'
    VIDEO = 'video'
    AUDIO = 'audio'
    WEB_PAGE = 'web_page'