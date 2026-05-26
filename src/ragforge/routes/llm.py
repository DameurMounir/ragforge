import logging

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from src.ragforge.core.config import Settings, get_settings
from src.ragforge.providers.llm.exceptions import (
    LLMConfigurationError,
    LLMProviderError,
)
from src.ragforge.providers.llm.schemas import (
    LLMGenerationRequest,
    LLMGenerationResponse,
)
from src.ragforge.services.llm_service import LLMService


logger = logging.getLogger('uvicorn.error')


llm_router = APIRouter(
    prefix='/api/v1/llm',
    tags=['llm'],
)


@llm_router.post(
    '/generate',
    response_model=LLMGenerationResponse,
)
async def generate_llm_response(
    generation_request: LLMGenerationRequest,
    app_settings: Settings = Depends(get_settings),
):
    """
    Generate a provider-neutral LLM response.

    This endpoint is intentionally simple in Branch 14.
    It validates the LLM Factory before vector search and RAG answers exist.
    """

    service = LLMService(settings=app_settings)

    try:
        return await service.generate(request=generation_request)

    except LLMConfigurationError as error:
        logger.error(f'LLM configuration error: {error}')
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'signal': 'llm_configuration_error',
                'message': str(error),
            },
        )

    except LLMProviderError as error:
        logger.error(f'LLM provider error: {error}')
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={
                'signal': 'llm_provider_error',
                'message': str(error),
            },
        )

    except Exception as error:
        logger.exception(f'Unexpected LLM generation error: {error}')
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                'signal': 'llm_generation_failed',
                'message': str(error),
            },
        )