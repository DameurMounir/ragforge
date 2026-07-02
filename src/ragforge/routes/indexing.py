from fastapi import APIRouter, Depends, Request, Security
from fastapi.responses import JSONResponse

from src.ragforge.core.config import Settings, get_settings
from src.ragforge.schemas.indexing import IndexingRequest, IndexingResponse
from src.ragforge.security.service_auth import require_service_identity
from src.ragforge.services.indexing_service import IndexingService
from src.ragforge.stores.mongodb.chunk_store import ChunkStore
from src.ragforge.stores.mongodb.project_store import ProjectStore


indexing_router = APIRouter(
    prefix="/api/v1/indexing",
    tags=["indexing"],
    dependencies=[Security(require_service_identity)],
)


@indexing_router.post("/{project_id}", response_model=IndexingResponse)
async def index_project_chunks(
    request: Request,
    project_id: str,
    indexing_request: IndexingRequest,
    app_settings: Settings = Depends(get_settings),
) -> IndexingResponse | JSONResponse:
    """Index stored project chunks into the configured vector backend."""

    project_store = await ProjectStore.create_instance(db_client=request.app.db_client)
    chunk_store = await ChunkStore.create_instance(db_client=request.app.db_client)
    status_code, response = await IndexingService(
        settings=app_settings
    ).index_project_chunks(
        project_id=project_id,
        indexing_request=indexing_request,
        project_store=project_store,
        chunk_store=chunk_store,
    )
    if 200 <= status_code < 300:
        return IndexingResponse.model_validate(response)
    return JSONResponse(status_code=status_code, content=response)
