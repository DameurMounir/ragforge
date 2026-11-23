from unittest import TestCase
from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.ragforge.routes import documents


class ProcessedAssetWireTests(TestCase):
    def test_conditional_chunks_preserve_other_default_fields(self):
        for chunk_fields in ({}, {"chunks": []}, {"chunks": [{"text": "Excerpt"}]}):
            with self.subTest(chunk_fields=chunk_fields):
                self.check_http_response(chunk_fields)

    def check_http_response(self, chunk_fields):
        asset = {
            "asset_id": "asset-1",
            "asset_name": "notes.txt",
            "status": "processed",
            "inserted_chunks": 1,
        }
        payload = {
            "signal": "document_processing_success",
            "message": "Processing completed.",
            "project_id": "project-1",
            "mode": "single_asset_by_id",
            "chunk_size": 1000,
            "overlap_size": 200,
            "do_reset": False,
            "processed_files": 1,
            "failed_files": 0,
            "skipped_files": 0,
            "inserted_chunks": 1,
            "deleted_chunks": 0,
            "processed_assets": [{**asset, **chunk_fields}],
        }
        app = FastAPI()
        app.db_client = object()
        app.include_router(documents.documents_router)
        app.dependency_overrides[documents.require_service_identity] = lambda: None

        with (
            patch.object(documents.ProjectStore, "create_instance", new_callable=AsyncMock),
            patch.object(documents.AssetStore, "create_instance", new_callable=AsyncMock),
            patch.object(documents.ChunkStore, "create_instance", new_callable=AsyncMock),
            patch.object(documents, "PipelineService") as pipeline,
            TestClient(app) as client,
        ):
            pipeline.return_value.process_project_documents = AsyncMock(return_value=(200, payload))
            response = client.post(
                "/api/v1/documents/process/project-1",
                json={"asset_id": "asset-1", "include_chunks": "chunks" in chunk_fields},
            )

        self.assertEqual(response.status_code, 200)
        expected = {
            **payload,
            "processed_assets": [{**asset, "file_name": None, **chunk_fields}],
            "failed_assets": [],
            "skipped_assets": [],
        }
        self.assertEqual(response.json(), expected)
