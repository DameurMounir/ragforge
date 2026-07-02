from fastapi import APIRouter, Depends, Request, Security
from fastapi.responses import JSONResponse

from src.ragforge.core.config import Settings, get_settings
from src.ragforge.schemas.answers import RAGAnswerRequest, RAGAnswerResponse
from src.ragforge.security.service_auth import require_service_identity
from src.ragforge.services.rag_answer_service import RAGAnswerService
from src.ragforge.stores.mongodb.project_store import ProjectStore


answers_router = APIRouter(
    prefix="/api/v1/answers",
    tags=["answers"],
    dependencies=[Security(require_service_identity)],
)


@answers_router.post("/{project_id}", response_model=RAGAnswerResponse)
async def answer_project_question(
    request: Request,
    project_id: str,
    answer_request: RAGAnswerRequest,
    app_settings: Settings = Depends(get_settings),
) -> RAGAnswerResponse | JSONResponse:
    """Generate a grounded answer from indexed project evidence."""

    project_store = await ProjectStore.create_instance(db_client=request.app.db_client)
    status_code, response = await RAGAnswerService(
        settings=app_settings
    ).answer_project_question(
        project_id=project_id,
        answer_request=answer_request,
        project_store=project_store,
    )
    if 200 <= status_code < 300:
        return RAGAnswerResponse.model_validate(response)
    return JSONResponse(status_code=status_code, content=response)
