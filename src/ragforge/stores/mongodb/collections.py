from enum import Enum


class MongoCollection(str, Enum):
    """
    MongoDB collection names used by RAGForge.
    """

    PROJECTS = 'projects'
    ASSETS = 'assets'
    DATA_CHUNKS = 'data_chunks'