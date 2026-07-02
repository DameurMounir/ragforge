from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from src.ragforge.core.config import Settings, get_settings
from src.ragforge.models.enums.response_signals import ResponseSignal
from src.ragforge.schemas.health import HealthResponse


health_router = APIRouter(prefix="/api/v1", tags=["health"])


@health_router.get("/health/", response_model=HealthResponse)
async def health(app_settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Public liveness endpoint; it exposes no tenant or knowledge data."""

    return HealthResponse(
        signal=ResponseSignal.APP_HEALTHY.value,
        status="healthy",
        app_name=app_settings.APP_NAME,
        app_version=app_settings.APP_VERSION,
        environment=app_settings.APP_ENV,
        timestamp=datetime.now(timezone.utc),
    )
