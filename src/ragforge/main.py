from fastapi import FastAPI 
from dotenv import load_dotenv
from src.ragforge.routes.base import base_router
from src.ragforge.routes.health import health_router


load_dotenv(".env")
app = FastAPI()


app.include_router(base_router)
app.include_router(health_router)
