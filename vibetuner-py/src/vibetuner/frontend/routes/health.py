import os
from datetime import datetime

from fastapi import APIRouter

from vibetuner.config import settings
from vibetuner.paths import root as root_path


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
    if root_path is None:
        raise RuntimeError(
            "Project root not detected. Cannot provide instance information."
        )
    return {
        "app": settings.project.project_slug,
        "port": int(os.environ.get("PORT", 8000)),
        "debug": settings.debug,
        "status": "healthy",
        "root_path": str(root_path.resolve()),
        "process_id": os.getpid(),
        "startup_time": _startup_time.isoformat(),
    }
