from streaq import Worker

from .._config import project_settings
from .context import lifespan


worker = Worker(redis_url=str(project_settings.redis_url), worker_lifespan=lifespan)
