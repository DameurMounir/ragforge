import logging
from datetime import datetime, timezone
from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, File, Request, Security, UploadFile, status
from fastapi.responses import JSONResponse

from src.ragforge.core.config import Settings, get_settings
from src.ragforge.models import ResponseSignal
from src.ragforge.models.db_schemes import Asset
from src.ragforge.models.enums.asset_status import AssetStatus
from src.ragforge.models.enums.asset_type import AssetType
from src.ragforge.schemas.document_processing import (
    ProcessDocumentRequest,
    ProcessDocumentResponse,
)
from src.ragforge.schemas.documents import UploadDocumentResponse
from src.ragforge.security.service_auth import require_service_identity
from src.ragforge.services.document_service import DocumentService
from src.ragforge.services.pipeline_service import PipelineService
from src.ragforge.stores.mongodb import AssetStore, ChunkStore, ProjectStore


logger = logging.getLogger("uvicorn.error")


documents_router = APIRouter(
    prefix="/api/v1/documents",
    tags=["documents"],
    dependencies=[Security(require_service_identity)],
)


@documents_router.post(
    "/upload/{project_id}",
    response_model=UploadDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    request: Request,
    project_id: str,
    file: UploadFile = File(...),
    app_settings: Settings = Depends(get_settings),
) -> UploadDocumentResponse | JSONResponse:
    """Upload one document and persist its asset metadata."""

    document_service = DocumentService()
    is_valid, result_signal = document_service.validate_uploaded_file(file=file)
    original_filename = file.filename
    if not is_valid or not original_filename:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": result_signal, "message": "File validation failed."},
        )

    try:
        file_path, document_id, stored_filename = (
            document_service.generate_unique_file_path(
                original_filename=original_filename,
                project_id=project_id,
            )
        )
        async with aiofiles.open(file_path, "wb") as output_file:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await output_file.write(chunk)

        file_size = Path(file_path).stat().st_size
        file_extension = Path(original_filename).suffix.replace(".", "").lower()
        project_store = await ProjectStore.create_instance(
            db_client=request.app.db_client
        )
        asset_store = await AssetStore.create_instance(db_client=request.app.db_client)
        project = await project_store.get_project_or_create_one(project_id=project_id)
        asset = Asset(
            asset_project_id=project.id,
            asset_type=AssetType.FILE,
            asset_status=AssetStatus.UPLOADED,
            asset_name=stored_filename,
            source_uri=str(file_path),
            file_name=original_filename,
            file_extension=file_extension,
            mime_type=file.content_type,
            asset_size=file_size,
            storage_path=str(file_path),
        )
        asset_record = await asset_store.create_asset(asset=asset)
    except ValueError as error:
        logger.error("Invalid upload request: %s", error)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_VALIDATION_FAILED.value,
                "message": str(error),
            },
        )
    except Exception:
        logger.exception("Error while uploading document")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value,
                "message": "Document upload failed.",
            },
        )

    return UploadDocumentResponse(
        signal=ResponseSignal.FILE_UPLOAD_SUCCESS.value,
        message="Document uploaded successfully.",
        document_id=document_id,
        asset_id=str(asset_record.id),
        project_id=project_id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        content_type=file.content_type,
        file_size=file_size,
        uploaded_at=datetime.now(timezone.utc),
    )


@documents_router.post(
    "/process/{project_id}",
    response_model=ProcessDocumentResponse,
)
async def process_document(
    request: Request,
    project_id: str,
    process_request: ProcessDocumentRequest,
) -> ProcessDocumentResponse | JSONResponse:
    """Process one document or all project documents."""

    project_store = await ProjectStore.create_instance(db_client=request.app.db_client)
    asset_store = await AssetStore.create_instance(db_client=request.app.db_client)
    chunk_store = await ChunkStore.create_instance(db_client=request.app.db_client)
    status_code, response = await PipelineService().process_project_documents(
        project_id=project_id,
        process_request=process_request,
        project_store=project_store,
        asset_store=asset_store,
        chunk_store=chunk_store,
    )
    if 200 <= status_code < 300:
        return ProcessDocumentResponse.model_validate(response)
    return JSONResponse(status_code=status_code, content=response)
