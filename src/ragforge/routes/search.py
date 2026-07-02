from fastapi import APIRouter, Request, Security
from fastapi.responses import JSONResponse

from src.ragforge.core.config import get_settings
from src.ragforge.schemas.search import SemanticSearchRequest, SemanticSearchResponse
from src.ragforge.security.service_auth import require_service_identity
from src.ragforge.services.semantic_search_service import SemanticSearchService
from src.ragforge.stores.mongodb.project_store import ProjectStore


search_router = APIRouter(
    prefix="/api/v1/search",
    tags=["search"],
    dependencies=[Security(require_service_identity)],
)


@search_router.post("/{project_id}", response_model=SemanticSearchResponse)
async def semantic_search(
    project_id: str,
    search_request: SemanticSearchRequest,
    request: Request,
) -> SemanticSearchResponse | JSONResponse:
    """Return ranked evidence from indexed project chunks."""

    project_store = await ProjectStore.create_instance(db_client=request.app.db_client)
    status_code, response = await SemanticSearchService(
        settings=get_settings()
    ).search_project_chunks(
        project_id=project_id,
        search_request=search_request,
        project_store=project_store,
    )
    if 200 <= status_code < 300:
        return SemanticSearchResponse.model_validate(response)
    return JSONResponse(status_code=status_code, content=response)
