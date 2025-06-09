from streaq import Worker
from streaq.constants import DEFAULT_QUEUE_NAME

from .._config import project_settings, settings
from .context import lifespan


print(settings.debug)

worker = Worker(
    redis_url=str(project_settings.redis_url),
    queue_name=("debug" if settings.debug else DEFAULT_QUEUE_NAME),
    worker_lifespan=lifespan,
)
