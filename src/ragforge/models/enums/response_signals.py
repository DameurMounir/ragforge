# Import Enum to create controlled response signal values.
from enum import Enum


# ResponseSignal defines standard API signals used across RAGForge.
# These signals help keep API responses predictable and easy to handle
# by frontend apps, clients, workers, and future agentic layers.
class ResponseSignal(str, Enum):
    # General application signals.
    APP_HEALTHY = 'app_healthy'
    INTERNAL_SERVER_ERROR = 'internal_server_error'

    # Project signals.
    PROJECT_NOT_FOUND = 'project_not_found'

    # Asset signals.
    ASSET_NOT_FOUND = 'asset_not_found'
    NO_FILES_TO_PROCESS = 'no_files_to_process'

    # File validation signals.
    FILE_VALIDATION_SUCCESS = 'file_validation_success'
    FILE_TYPE_NOT_SUPPORTED = 'file_type_not_supported'
    FILE_SIZE_EXCEEDED = 'file_size_exceeded'
    FILE_VALIDATION_FAILED = 'file_validation_failed'

    # File upload signals.
    FILE_UPLOAD_SUCCESS = 'file_upload_success'
    FILE_UPLOAD_FAILED = 'file_upload_failed'

    # Document processing signals.
    DOCUMENT_NOT_FOUND = 'document_not_found'
    DOCUMENT_PROCESSING_SUCCESS = 'document_processing_success'
    DOCUMENT_PROCESSING_PARTIAL_SUCCESS = (
        'document_processing_partial_success'
    )
    DOCUMENT_PROCESSING_FAILED = 'document_processing_failed'
    DOCUMENT_TYPE_NOT_SUPPORTED = 'document_type_not_supported'
    DOCUMENT_EMPTY_CONTENT = 'document_empty_content'

    #indexing 
    INDEXING_SUCCESS = 'indexing_success'
    INDEXING_PARTIAL_SUCCESS = 'indexing_partial_success'
    INDEXING_FAILED = 'indexing_failed'
    NO_CHUNKS_TO_INDEX = 'no_chunks_to_index'
    
    #Branch 17 semantic search 
    SEMANTIC_SEARCH_SUCCESS = 'semantic_search_success'
    SEMANTIC_SEARCH_FAILED = 'semantic_search_failed'
    SEMANTIC_SEARCH_NO_RESULTS = 'semantic_search_no_results'
    SEARCH_QUERY_EMPTY = 'search_query_empty'

    # Branch 18 grounded answer signals.
    RAG_ANSWER_SUCCESS = 'rag_answer_success'
    RAG_ANSWER_FAILED = 'rag_answer_failed'
    RAG_ANSWER_NO_CONTEXT = 'rag_answer_no_context'