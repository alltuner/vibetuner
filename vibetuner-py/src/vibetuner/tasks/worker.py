from streaq import Worker

from vibetuner.config import settings
from vibetuner.tasks.lifespan import lifespan


worker: Worker | None = (
    Worker(
        redis_url=str(settings.redis_url),
        queue_name=settings.redis_key_prefix.rstrip(":"),
        lifespan=lifespan,
        concurrency=settings.worker_concurrency,
    )
    if settings.workers_available
    else None
)
