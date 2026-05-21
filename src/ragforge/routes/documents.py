import logging
from datetime import datetime, timezone
from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, File, Request, UploadFile, status
from fastapi.responses import JSONResponse

from src.ragforge.core.config import Settings, get_settings
from src.ragforge.models import ResponseSignal
from src.ragforge.models.db_schemes import Asset, DataChunk
from src.ragforge.models.enums.asset_status import AssetStatus
from src.ragforge.models.enums.asset_type import AssetType
from src.ragforge.schemas.document_processing import ProcessDocumentRequest
from src.ragforge.services.document_processing_service import DocumentProcessingService
from src.ragforge.services.document_service import DocumentService
from src.ragforge.stores.mongodb import AssetStore, ChunkStore, ProjectStore


logger = logging.getLogger('uvicorn.error')


documents_router = APIRouter(
    prefix='/api/v1/documents',
    tags=['documents']
)


@documents_router.post('/upload/{project_id}')
async def upload_document(
    request: Request,
    project_id: str,
    file: UploadFile = File(...),
    app_settings: Settings = Depends(get_settings),
):
    """
    Upload a document into a project-based storage folder and persist asset metadata.

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
                'message': 'File validation failed.',
            },
        )

    try:
        file_path, document_id, stored_filename = (
            document_service.generate_unique_file_path(
                original_filename=file.filename,
                project_id=project_id,
            )
        )

        async with aiofiles.open(file_path, 'wb') as output_file:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await output_file.write(chunk)

        file_size = Path(file_path).stat().st_size
        file_extension = Path(file.filename).suffix.replace('.', '').lower()

        db_client = request.app.db_client

        project_store = await ProjectStore.create_instance(
            db_client=db_client
        )
        asset_store = await AssetStore.create_instance(
            db_client=db_client
        )

        project = await project_store.get_project_or_create_one(
            project_id=project_id
        )

        asset = Asset(
            asset_project_id=project.id,
            asset_type=AssetType.FILE.value,
            asset_status=AssetStatus.UPLOADED.value,
            asset_name=stored_filename,
            source_uri=str(file_path),
            file_name=file.filename,
            file_extension=file_extension,
            mime_type=file.content_type,
            asset_size=file_size,
            storage_path=str(file_path),
        )

        asset_record = await asset_store.create_asset(asset=asset)

    except ValueError as error:
        logger.error(f'Invalid upload request: {error}')

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'signal': ResponseSignal.FILE_VALIDATION_FAILED.value,
                'message': str(error),
            },
        )

    except Exception as error:
        logger.error(f'Error while uploading document: {error}')

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                'signal': ResponseSignal.FILE_UPLOAD_FAILED.value,
                'message': str(error),
            },
        )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            'signal': ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            'message': 'Document uploaded successfully.',
            'document_id': document_id,
            'asset_id': str(asset_record.id),
            'project_id': project_id,
            'original_filename': file.filename,
            'stored_filename': stored_filename,
            'content_type': file.content_type,
            'file_size': file_size,
            'uploaded_at': datetime.now(timezone.utc).isoformat(),
        },
    )


@documents_router.post('/process/{project_id}')
async def process_document(
    request: Request,
    project_id: str,
    process_request: ProcessDocumentRequest,
):
    """
    Process an uploaded document, split it into chunks, persist chunks,
    and update asset processing metadata.
    """

    document_processing_service = DocumentProcessingService()

    db_client = request.app.db_client

    project_store = await ProjectStore.create_instance(
        db_client=db_client
    )
    asset_store = await AssetStore.create_instance(
        db_client=db_client
    )
    chunk_store = await ChunkStore.create_instance(
        db_client=db_client
    )

    project = await project_store.get_project_by_project_id(
        project_id=project_id
    )

    if project is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'signal': ResponseSignal.DOCUMENT_NOT_FOUND.value,
                'message': 'Project not found.',
            },
        )

    asset = await asset_store.get_asset_record(
        asset_project_id=project.id,
        asset_name=process_request.stored_filename,
    )

    if asset is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'signal': ResponseSignal.DOCUMENT_NOT_FOUND.value,
                'message': 'Asset metadata not found.',
            },
        )

    try:
        chunks = document_processing_service.process_document(
            project_id=project_id,
            stored_filename=process_request.stored_filename,
            chunk_size=process_request.chunk_size,
            overlap_size=process_request.overlap_size,
        )

    except FileNotFoundError:
        await asset_store.update_asset_processing_result(
            asset_id=asset.id,
            asset_status=AssetStatus.FAILED.value,
            chunk_count=0,
            extraction_method=None,
            extraction_error='Document not found.',
        )

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'signal': ResponseSignal.DOCUMENT_NOT_FOUND.value,
                'message': 'Document not found.',
            },
        )

    except ValueError as error:
        await asset_store.update_asset_processing_result(
            asset_id=asset.id,
            asset_status=AssetStatus.FAILED.value,
            chunk_count=0,
            extraction_method=None,
            extraction_error=str(error),
        )

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'signal': ResponseSignal.DOCUMENT_TYPE_NOT_SUPPORTED.value,
                'message': str(error),
            },
        )

    except Exception as error:
        await asset_store.update_asset_processing_result(
            asset_id=asset.id,
            asset_status=AssetStatus.FAILED.value,
            chunk_count=0,
            extraction_method=None,
            extraction_error=str(error),
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                'signal': ResponseSignal.DOCUMENT_PROCESSING_FAILED.value,
                'message': str(error),
            },
        )

    if not chunks:
        await asset_store.update_asset_processing_result(
            asset_id=asset.id,
            asset_status=AssetStatus.FAILED.value,
            chunk_count=0,
            extraction_method=None,
            extraction_error='Document content is empty.',
        )

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'signal': ResponseSignal.DOCUMENT_EMPTY_CONTENT.value,
                'message': 'Document content is empty.',
            },
        )

    data_chunks = []

    for index, chunk in enumerate(chunks, start=1):
        if isinstance(chunk, dict):
            chunk_text = (
                chunk.get('chunk_text')
                or chunk.get('text')
                or chunk.get('page_content')
                or str(chunk)
            )
            chunk_metadata = chunk.get('metadata', {})
        else:
            chunk_text = getattr(chunk, 'page_content', str(chunk))
            chunk_metadata = getattr(chunk, 'metadata', {})

        data_chunks.append(
            DataChunk(
                chunk_text=chunk_text,
                chunk_metadata=chunk_metadata,
                chunk_order=index,
                chunk_project_id=project.id,
                chunk_asset_id=asset.id,
                embedded=False,
            )
        )

    await chunk_store.delete_chunks_by_asset_id(
        asset_id=asset.id
    )

    inserted_count = await chunk_store.insert_many_chunks(
        chunks=data_chunks
    )

    await asset_store.update_asset_processing_result(
        asset_id=asset.id,
        asset_status=AssetStatus.PROCESSED.value,
        chunk_count=inserted_count,
        extraction_method='document_processing_service',
        extraction_error=None,
    )

    return {
        'signal': ResponseSignal.DOCUMENT_PROCESSING_SUCCESS.value,
        'message': 'Document processed successfully.',
        'project_id': project_id,
        'asset_id': str(asset.id),
        'stored_filename': process_request.stored_filename,
        'chunk_size': process_request.chunk_size,
        'overlap_size': process_request.overlap_size,
        'chunk_count': inserted_count,
        'chunks': chunks,
    }