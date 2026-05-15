from fastapi import APIRouter
import os
from datetime import datetime,timezone

health_router=APIRouter(
    prefix='/api/v1/health',
    tags=['health']
)

@health_router.get('/')
async def health_check():
    app_name=os.getenv('APP_NAME')
    app_version = os.getenv('APP_VERSION')
    environment = os.getenv('APP_ENV')

    return {
        'status': 'healthy',
        'app_name': app_name,
        'app_version': app_version,
        'environment': environment,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }