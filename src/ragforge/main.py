from fastapi import FastAPI

from src.ragforge.core.config import get_settings
from src.ragforge.observability.metrics import setup_metrics
from src.ragforge.routes.base import base_router
from src.ragforge.routes.health import health_router
from src.ragforge.routes.documents import documents_router
from src.ragforge.stores.mongodb.client import MongoDBClient

from src.ragforge.routes.llm import llm_router
from src.ragforge.routes.indexing import indexing_router
from src.ragforge.routes.search import search_router

from src.ragforge.routes.answers import answers_router

from src.ragforge.stores.postgres.session import (
    PostgresConnectionSettings,
    PostgresSessionManager,
    build_postgres_async_url,
)


app = FastAPI()

settings = get_settings()
setup_metrics(app=app, settings=settings)


@app.on_event('startup')
async def startup_db_client():
    settings = get_settings()

    mongodb_client = MongoDBClient(settings=settings)
    await mongodb_client.connect()

    app.mongodb_client = mongodb_client
    app.db_client = mongodb_client.database

    postgres_connection = PostgresConnectionSettings.from_settings(settings)
    app.postgres_session_manager = PostgresSessionManager(
        database_url=build_postgres_async_url(postgres_connection),
        echo=settings.POSTGRES_ECHO,
        pool_size=settings.POSTGRES_POOL_SIZE,
        max_overflow=settings.POSTGRES_MAX_OVERFLOW,
        pool_timeout=settings.POSTGRES_POOL_TIMEOUT,
        pool_recycle=settings.POSTGRES_POOL_RECYCLE,
    )
    await app.postgres_session_manager.ping()

@app.on_event('shutdown')
async def shutdown_db_client():
    await app.mongodb_client.close()

    postgres_manager = getattr(app, 'postgres_session_manager', None)
    if postgres_manager is not None:
        await postgres_manager.dispose()


app.include_router(base_router)
app.include_router(health_router)
app.include_router(documents_router)
app.include_router(llm_router)
app.include_router(indexing_router)
app.include_router(search_router)
app.include_router(answers_router)