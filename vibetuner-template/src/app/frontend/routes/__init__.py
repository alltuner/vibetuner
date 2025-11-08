from fastapi import (
    APIRouter,
)

from vibetuner.frontend import register_router


app_router = APIRouter()

register_router(app_router)
