from streaq import Worker

from vibetuner.config import settings
from vibetuner.tasks.lifespan import lifespan


worker = Worker(
    redis_url=str(settings.redis_url),
    queue_name=(
        settings.project.project_slug
        if not settings.debug
        else f"debug-{settings.project.project_slug}"
    ),
    lifespan=lifespan,
)
