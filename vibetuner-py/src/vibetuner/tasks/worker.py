# ABOUTME: Streaq worker setup and configuration.
# ABOUTME: Creates the Worker instance used by CLI and task modules.
from typing import TYPE_CHECKING

from vibetuner.config import settings


if TYPE_CHECKING:
    from streaq import Worker


_worker: "Worker | None" = None
_initialized: bool = False


def _init_worker() -> "Worker | None":
    """Lazily create the Worker instance on first access."""
    global _worker, _initialized

    if _initialized:
        return _worker

    _initialized = True

    if not settings.workers_available:
        return None

    from vibetuner.extras import require_extra

    require_extra("worker", "Background task queue")

    from streaq import Worker as _Worker

    from vibetuner.tasks.lifespan import lifespan

    _worker = _Worker(
        redis_url=str(settings.redis_url),
        queue_name=settings.redis_key_prefix.rstrip(":"),
        lifespan=lifespan,
        concurrency=settings.worker_concurrency,
    )
    return _worker


def __getattr__(name: str):
    """Lazy module attribute for `worker` to support `vibetuner.tasks.worker:worker`."""
    if name == "worker":
        return _init_worker()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def get_worker() -> "Worker":
    """Get the worker instance, raising if workers are not configured.

    Use this instead of importing `worker` directly to get proper type checking:

        from vibetuner.tasks.worker import get_worker

        worker = get_worker()

        @worker.task()
        async def my_task():
            pass
    """
    w = _init_worker()
    if w is None:
        from vibetuner.services.errors import redis_not_configured

        raise RuntimeError(redis_not_configured(log=False))
    return w
