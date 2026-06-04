from fastapi import FastAPI

from src.ragforge.core.config import get_settings
from src.ragforge.routes.base import base_router
from src.ragforge.routes.health import health_router
from src.ragforge.routes.documents import documents_router
from src.ragforge.stores.mongodb.client import MongoDBClient

from src.ragforge.routes.llm import llm_router
from src.ragforge.routes.indexing import indexing_router
from src.ragforge.routes.search import search_router


app = FastAPI()


@app.on_event('startup')
async def startup_db_client():
    settings = get_settings()

    mongodb_client = MongoDBClient(settings=settings)
    await mongodb_client.connect()

    app.mongodb_client = mongodb_client
    app.db_client = mongodb_client.database


@app.on_event('shutdown')
async def shutdown_db_client():
    await app.mongodb_client.close()


app.include_router(base_router)
app.include_router(health_router)
app.include_router(documents_router)
app.include_router(llm_router)
app.include_router(indexing_router)
app.include_router(search_router)