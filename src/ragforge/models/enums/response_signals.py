# Import Enum to create controlled response signal values.
from enum import Enum


# ResponseSignal defines standard API signals used across RAGForge.
# These signals help keep API responses predictable and easy to handle
# by frontend apps, clients, workers, and future agentic layers.
class ResponseSignal(str, Enum):
    # General application signals.
    APP_HEALTHY = 'app_healthy'

    # File validation signals.
    FILE_VALIDATION_SUCCESS = 'file_validation_success'
    FILE_TYPE_NOT_SUPPORTED = 'file_type_not_supported'
    FILE_SIZE_EXCEEDED = 'file_size_exceeded'
    FILE_VALIDATION_FAILED = 'file_validation_failed'

    # File upload signals.
    FILE_UPLOAD_SUCCESS = 'file_upload_success'
    FILE_UPLOAD_FAILED = 'file_upload_failed'

    # Generic error signal.
    INTERNAL_SERVER_ERROR = 'internal_server_error'