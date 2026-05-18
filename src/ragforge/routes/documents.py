import logging
from datetime import datetime, timezone

import aiofiles
from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import JSONResponse

from src.ragforge.core.config import Settings, get_settings
from src.ragforge.models import ResponseSignal
from src.ragforge.services.document_service import DocumentService

from src.ragforge.schemas.document_processing import ProcessDocumentRequest
from src.ragforge.services.document_processing_service import DocumentProcessingService


logger = logging.getLogger('uvicorn.error')


documents_router = APIRouter(
    prefix='/api/v1/documents',
    tags=['documents']
)


@documents_router.post('/upload/{project_id}')
async def upload_document(
    project_id: str,
    file: UploadFile = File(...),
    app_settings: Settings = Depends(get_settings)
):
    """
    Upload a document into a project-based storage folder.

    Final storage structure:
    storage/uploads/{project_id}/documents/{document_id}_{filename}
    """

    document_service = DocumentService()

    is_valid, result_signal = document_service.validate_uploaded_file(file=file)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'signal': result_signal,
                'message': 'File validation failed.'
            }
        )

    try:
        file_path, document_id, stored_filename = (
            document_service.generate_unique_file_path(
                original_filename=file.filename,
                project_id=project_id
            )
        )

        async with aiofiles.open(file_path, 'wb') as output_file:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await output_file.write(chunk)

    except ValueError as error:
        logger.error(f'Invalid upload request: {error}')

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'signal': ResponseSignal.FILE_VALIDATION_FAILED.value,
                'message': str(error)
            }
        )

    except Exception as error:
        logger.error(f'Error while uploading document: {error}')

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                'signal': ResponseSignal.FILE_UPLOAD_FAILED.value,
                'message': 'Document upload failed.'
            }
        )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            'signal': ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            'message': 'Document uploaded successfully.',
            'document_id': document_id,
            'project_id': project_id,
            'original_filename': file.filename,
            'stored_filename': stored_filename,
            'content_type': file.content_type,
            'file_size': file.size,
            'uploaded_at': datetime.now(timezone.utc).isoformat()
        }
    )

@documents_router.post('/process/{project_id}')
async def process_document(
    project_id: str,
    process_request: ProcessDocumentRequest,
):
    """
    Process an uploaded document and split it into chunks.
    """
    document_processing_service = DocumentProcessingService()

    try:
        chunks = document_processing_service.process_document(
            project_id=project_id,
            stored_filename=process_request.stored_filename,
            chunk_size=process_request.chunk_size,
            overlap_size=process_request.overlap_size,
        )

    except FileNotFoundError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'signal': ResponseSignal.DOCUMENT_NOT_FOUND.value,
                'message': 'Document not found.',
            },
        )

    except ValueError as error:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'signal': ResponseSignal.DOCUMENT_TYPE_NOT_SUPPORTED.value,
                'message': str(error),
            },
        )

    except Exception as error:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                'signal': ResponseSignal.DOCUMENT_PROCESSING_FAILED.value,
                'message': str(error),
            },
        )

    if not chunks:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'signal': ResponseSignal.DOCUMENT_EMPTY_CONTENT.value,
                'message': 'Document content is empty.',
            },
        )

    return {
        'signal': ResponseSignal.DOCUMENT_PROCESSING_SUCCESS.value,
        'message': 'Document processed successfully.',
        'project_id': project_id,
        'stored_filename': process_request.stored_filename,
        'chunk_size': process_request.chunk_size,
        'overlap_size': process_request.overlap_size,
        'chunk_count': len(chunks),
        'chunks': chunks,
    }
    