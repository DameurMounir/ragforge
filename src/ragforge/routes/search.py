from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from src.ragforge.core.config import get_settings
from src.ragforge.schemas.search import SemanticSearchRequest
from src.ragforge.services.semantic_search_service import (
    SemanticSearchService,
)
from src.ragforge.stores.mongodb.project_store import ProjectStore


search_router = APIRouter(
    prefix='/api/v1/search',
    tags=['search'],
)


@search_router.post('/{project_id}')
async def semantic_search(
    project_id: str,
    search_request: SemanticSearchRequest,
    request: Request,
):
    """
    Search indexed chunks for a project and return ranked evidence.

    This endpoint is intentionally retrieval-only.
    Branch 18 will consume the evidence returned here to generate grounded
    answers with sources.
    """

    project_store = await ProjectStore.create_instance(
        db_client=request.app.db_client
    )

    service = SemanticSearchService(settings=get_settings())

    status_code, response = await service.search_project_chunks(
        project_id=project_id,
        search_request=search_request,
        project_store=project_store,
    )

    return JSONResponse(
        status_code=status_code,
        content=response,
    )
