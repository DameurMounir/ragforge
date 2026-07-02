from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    signal: Literal["app_healthy"]
    status: Literal["healthy"]
    app_name: str
    app_version: str
    environment: str
    timestamp: datetime
