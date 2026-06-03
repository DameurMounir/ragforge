from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from src.ragforge.core.config import Settings, get_settings
from src.ragforge.schemas.indexing import IndexingRequest
from src.ragforge.services.indexing_service import IndexingService
from src.ragforge.stores.mongodb.chunk_store import ChunkStore
from src.ragforge.stores.mongodb.project_store import ProjectStore


indexing_router = APIRouter(
    prefix='/api/v1/indexing',
    tags=['indexing'],
)


@indexing_router.post('/{project_id}')
async def index_project_chunks(
    request: Request,
    project_id: str,
    indexing_request: IndexingRequest,
    app_settings: Settings = Depends(get_settings),
):
    """
    Index stored MongoDB chunks into Qdrant.

    Branch 16:
    - reads DataChunk records,
    - generates embeddings,
    - stores vectors in Qdrant,
    - marks chunks as embedded.

    This endpoint does not perform semantic search yet.
    """

    db_client = request.app.db_client

    project_store = await ProjectStore.create_instance(db_client=db_client)
    chunk_store = await ChunkStore.create_instance(db_client=db_client)

    indexing_service = IndexingService(settings=app_settings)

    status_code, response = await indexing_service.index_project_chunks(
        project_id=project_id,
        indexing_request=indexing_request,
        project_store=project_store,
        chunk_store=chunk_store,
    )

    return JSONResponse(
        status_code=status_code,
        content=response,
    )
