from fastapi import FastAPI
from app.core.config import get_settings

# Import all models here so SQLAlchemy relationship registry is fully populated
import app.db.init_db  # noqa: F401

from app.api.v1 import api_router

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version="0.1.0",
)

app.include_router(api_router)