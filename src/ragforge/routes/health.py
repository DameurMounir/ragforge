# Import datetime and timezone to generate a UTC timestamp.
from datetime import datetime, timezone

# Import APIRouter to create a separated group of health-related routes.
# Import Depends to inject dependencies into route functions.
from fastapi import APIRouter, Depends

# Import Settings type and get_settings function from core/config.py.
from src.ragforge.core.config import Settings, get_settings

# Import ResponseSignal to standardize API response signals.
from src.ragforge.models.enums.response_signals import ResponseSignal


# Create the health router.
# prefix='/api/v1' means all routes here start with /api/v1.
# tags=['health'] is used in Swagger/OpenAPI documentation.
health_router = APIRouter(
    prefix='/api/v1',
    tags=['health']
)


# Define the health check endpoint.
# Final URL:
# GET http://127.0.0.1:8000/api/v1/health/
@health_router.get('/health/')
async def health(app_settings: Settings = Depends(get_settings)):
    # app_settings is automatically injected by FastAPI.
    # FastAPI calls get_settings() and provides the Settings object here.

    # Return a standardized JSON response showing that the API is running correctly.
    return {
        'signal': ResponseSignal.APP_HEALTHY.value,
        'status': 'healthy',
        'app_name': app_settings.APP_NAME,
        'app_version': app_settings.APP_VERSION,
        'environment': app_settings.APP_ENV,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }