from streaq import Worker

from ..core.config import project_settings, settings
from .context import lifespan


worker = Worker(
    redis_url=str(project_settings.redis_url),
    queue_name=(
        project_settings.project_slug
        if not settings.debug
        else f"debug-{project_settings.project_slug}"
    ),
    lifespan=lifespan,
)

# Register tasks
# use something like from . import task_module_name // noqa: E402, F401
