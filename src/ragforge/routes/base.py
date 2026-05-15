# Import APIRouter to create a group of related API routes.
# Import Depends to inject dependencies into route functions.
from fastapi import APIRouter, Depends

# Import datetime and timezone to generate a UTC timestamp in the response.
from datetime import datetime, timezone

# Import Settings type and get_settings function from core/config.py.
from src.ragforge.core.config import Settings, get_settings


# Create the base router.
# prefix='/api/v1' means every endpoint inside this router starts with /api/v1.
# tags=['base'] is used only for Swagger/OpenAPI documentation.
base_router = APIRouter(
    prefix='/api/v1',
    tags=['base']
)


# Define the root endpoint for API v1.
# Final URL:
# GET http://127.0.0.1:8000/api/v1/
@base_router.get('/')
async def hello(app_settings: Settings = Depends(get_settings)):
    # app_settings is automatically injected by FastAPI.
    # FastAPI calls get_settings() and provides the Settings object here.

    # Return a clean JSON response.
    return {
        'message': 'Hello and goodbye!',
        'app_name': app_settings.APP_NAME,
        'app_version': app_settings.APP_VERSION,
        'environment': app_settings.APP_ENV,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }