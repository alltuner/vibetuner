from streaq import Worker

from vibetuner.config import settings
from vibetuner.tasks.lifespan import lifespan


_worker: Worker | None = (
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
    if _worker is None:
        raise RuntimeError(
            "Workers not configured. Set REDIS_URL and ensure workers are enabled."
        )
    return _worker


# Backwards compatibility alias
worker = _worker
