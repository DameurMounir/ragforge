from fastapi import APIRouter
import os 

base_router = APIRouter(
    prefix="/api/v1",
    tags=["/api/v1"]
)

@base_router.get("/")

async def hello():
    app_name = os.getenv('APP_NAME')
    app_version = os.getenv('APP_VERSION')
    return {
            "message": "Hello and goodbye!",
            "app_name":app_name,
            "app_version":app_version,
    }

