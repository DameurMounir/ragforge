from unittest.mock import AsyncMock, Mock

import pytest
from bson import ObjectId

from src.ragforge.models.db_schemes import Asset, Project
from src.ragforge.schemas.document_processing import ProcessDocumentRequest
from src.ragforge.services.pipeline_service import PipelineService


@pytest.mark.anyio
async def test_partial_chunk_store_write_stays_failed_until_complete_retry():
    project = Project(_id=ObjectId(), project_id="corpus")
    asset = Asset(_id=ObjectId(), asset_project_id=project.id, asset_name="manual.txt")
    projects, assets, chunks = AsyncMock(), AsyncMock(), AsyncMock()
    projects.get_project_by_project_id.return_value = project
    assets.get_asset_by_id.return_value = asset
    chunks.delete_chunks_by_asset_id.side_effect = [0, 1]
    chunks.insert_many_chunks.side_effect = [1, 2]
    request = ProcessDocumentRequest(asset_id=str(asset.id))
    service = PipelineService()
    service.document_processing_service.process_asset = Mock(
        return_value=[{"content": "First passage."}, {"content": "Second passage."}]
    )

    status, result = await service.process_project_documents("corpus", request, projects, assets, chunks)
    assert status == 500
    assert result["processed_assets"] == []
    assert result["failed_files"] == 1
    assert result["inserted_chunks"] == 1
    observed = assets.update_asset_processing_result.await_args_list
    assert [(call.kwargs["asset_status"], call.kwargs["chunk_count"]) for call in observed] == [
        ("processing", 0), ("failed", 0)
    ]

    status, retry = await service.process_project_documents("corpus", request, projects, assets, chunks)
    assert status == 200 and retry["failed_files"] == 0
    assert retry["deleted_chunks"] == 1 and retry["inserted_chunks"] == 2
    assert assets.update_asset_processing_result.await_args.kwargs["chunk_count"] == 2
    assert assets.update_asset_processing_result.await_args.kwargs["asset_status"] == "processed"
