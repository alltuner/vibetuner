from streaq import Worker
from vibetuner.tasks.context import lifespan

from app.config import settings


worker = Worker(
    redis_url=str(settings.project.redis_url),
    queue_name=(
        settings.project.project_slug
        if not settings.debug
        else f"debug-{settings.project.project_slug}"
    ),
    lifespan=lifespan,
)

# Register tasks
# use something like from . import task_module_name // noqa: E402, F401
