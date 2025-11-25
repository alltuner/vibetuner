from streaq import Worker

from vibetuner.config import settings
from vibetuner.tasks.lifespan import lifespan


worker = Worker(
    redis_url=str(settings.redis_url),
    queue_name=settings.redis_key_prefix.rstrip(":"),
    lifespan=lifespan,
)
