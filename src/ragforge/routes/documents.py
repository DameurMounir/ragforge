import logging
from datetime import datetime, timezone
from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, File, Request, UploadFile, status
from fastapi.responses import JSONResponse

from src.ragforge.core.config import Settings, get_settings
from src.ragforge.models import ResponseSignal
from src.ragforge.models.db_schemes import Asset
from src.ragforge.models.enums.asset_status import AssetStatus
from src.ragforge.models.enums.asset_type import AssetType
from src.ragforge.schemas.document_processing import ProcessDocumentRequest
from src.ragforge.services.document_service import DocumentService
from src.ragforge.services.pipeline_service import PipelineService
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
    Upload a document into a project-based storage folder
    and persist asset metadata.

    Final storage structure:
    storage/uploads/{project_id}/documents/{document_id}_{filename}
    """

    document_service = DocumentService()

    is_valid, result_signal = document_service.validate_uploaded_file(
        file=file
    )

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
            while chunk := await file.read(
                app_settings.FILE_DEFAULT_CHUNK_SIZE
            ):
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
    Process one document or all project documents.

    Branch 13 behavior:
    - asset_id provided        -> process one asset by MongoDB id
    - stored_filename provided -> process one asset by stored filename
    - neither provided         -> process all FILE assets in the project

    The route stays thin.
    Pipeline orchestration is delegated to PipelineService.
    """

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

    pipeline_service = PipelineService()

    status_code, response = await pipeline_service.process_project_documents(
        project_id=project_id,
        process_request=process_request,
        project_store=project_store,
        asset_store=asset_store,
        chunk_store=chunk_store,
    )

    return JSONResponse(
        status_code=status_code,
        content=response,
    )