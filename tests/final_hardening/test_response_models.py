from datetime import UTC, datetime

from src.ragforge.schemas.document_processing import ProcessDocumentResponse
from src.ragforge.schemas.documents import UploadDocumentResponse
from src.ragforge.schemas.health import HealthResponse


def test_health_and_upload_success_models_are_concrete() -> None:
    health = HealthResponse(
        signal="app_healthy",
        status="healthy",
        app_name="RAGForge",
        app_version="0.1.0",
        environment="test",
        timestamp=datetime.now(UTC),
    )
    upload = UploadDocumentResponse(
        signal="file_upload_success",
        message="ok",
        document_id="document",
        asset_id="asset",
        project_id="project",
        original_filename="input.txt",
        stored_filename="stored.txt",
        content_type="text/plain",
        file_size=5,
        uploaded_at=datetime.now(UTC),
    )
    assert health.status == "healthy"
    assert upload.file_size == 5


def test_processing_success_model_accepts_all_supported_modes() -> None:
    for mode in (
        "single_asset_by_id",
        "single_asset_by_filename",
        "all_project_file_assets",
    ):
        response = ProcessDocumentResponse(
            signal="document_processing_success",
            message="ok",
            project_id="project",
            mode=mode,
            chunk_size=1000,
            overlap_size=200,
            do_reset=False,
            processed_files=0,
            failed_files=0,
            skipped_files=0,
            inserted_chunks=0,
            deleted_chunks=0,
        )
        assert response.mode == mode
