# ABOUTME: Streaq worker setup and configuration.
# ABOUTME: Creates the Worker instance used by CLI and task modules.
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


def get_worker() -> Worker:
    """Get the worker instance, raising if workers are not configured.

    Use this instead of importing `worker` directly to get proper type checking:

        from vibetuner.tasks.worker import get_worker

        worker = get_worker()

        @worker.task()
        async def my_task():
            pass
    """
    if worker is None:
        from vibetuner.services.errors import redis_not_configured

        raise RuntimeError(redis_not_configured())
    return worker
