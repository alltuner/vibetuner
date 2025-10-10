import os
from datetime import datetime

from fastapi import APIRouter

from app.config import settings
from core.config import project_settings

from ...core import paths


router = APIRouter(prefix="/health")

# Store startup time for instance identification
_startup_time = datetime.now()


@router.get("/ping")
def health_ping():
    """Simple health check endpoint"""
    return {"ping": "ok"}


@router.get("/id")
def health_instance_id():
    """Instance identification endpoint for distinguishing app instances"""
    return {
        "app": project_settings.project_slug,
        "port": int(os.environ.get("PORT", 8000)),
        "debug": settings.debug,
        "status": "healthy",
        "root_path": str(paths.root.resolve()),
        "process_id": os.getpid(),
        "startup_time": _startup_time.isoformat(),
    }
