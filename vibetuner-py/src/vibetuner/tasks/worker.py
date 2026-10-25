# ABOUTME: Streaq worker setup and configuration.
# ABOUTME: Creates the Worker instance used by CLI and task modules.
from streaq import Worker

from vibetuner.config import settings
from vibetuner.context import Context
from vibetuner.tasks.lifespan import lifespan
from vibetuner.tasks.lua_names import use_versioned_names


# Every process that builds or enters a worker imports it from here: the
# worker, the frontend that enqueues, the CLIs and the streaq web UI.
use_versioned_names()

worker: Worker[Context] | None = (
    Worker(
        redis_url=str(settings.redis_url),
        redis_kwargs=settings.worker_redis_kwargs,
        queue_name=settings.redis_key_prefix.rstrip(":"),
        lifespan=lifespan,
        concurrency=settings.worker_concurrency,
        idle_timeout=settings.worker_idle_timeout,
    )
    if settings.workers_available
    else None
)


def get_worker() -> Worker[Context]:
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

        raise RuntimeError(redis_not_configured(log=False))
    return worker
