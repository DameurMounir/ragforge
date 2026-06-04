from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from src.ragforge.core.config import Settings, get_settings
from src.ragforge.schemas.answers import RAGAnswerRequest
from src.ragforge.services.rag_answer_service import RAGAnswerService
from src.ragforge.stores.mongodb.project_store import ProjectStore


answers_router = APIRouter(
    prefix='/api/v1/answers',
    tags=['answers'],
)


@answers_router.post('/{project_id}')
async def answer_project_question(
    request: Request,
    project_id: str,
    answer_request: RAGAnswerRequest,
    app_settings: Settings = Depends(get_settings),
):
    """
    Generate a grounded answer from indexed project evidence.

    Branch 18:
    - reuses Branch 17 semantic search,
    - builds controlled context,
    - calls LLMService,
    - returns answer with sources.
    """

    project_store = await ProjectStore.create_instance(
        db_client=request.app.db_client
    )

    service = RAGAnswerService(settings=app_settings)

    status_code, response = await service.answer_project_question(
        project_id=project_id,
        answer_request=answer_request,
        project_store=project_store,
    )

    return JSONResponse(
        status_code=status_code,
        content=response,
    )
