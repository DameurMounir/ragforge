from enum import Enum


class AssetStatus(str, Enum):
    """
    Processing lifecycle status for an asset.
    """

    UPLOADED = 'uploaded'
    REGISTERED = 'registered'
    PROCESSING = 'processing'
    PROCESSED = 'processed'
    FAILED = 'failed'
    INDEXED = 'indexed'