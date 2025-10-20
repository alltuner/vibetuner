from fastapi import (
    APIRouter,
)

from core.frontend import register_router


app_router = APIRouter()

register_router(app_router)
