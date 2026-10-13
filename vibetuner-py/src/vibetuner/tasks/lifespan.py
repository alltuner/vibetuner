# ABOUTME: Task worker lifespan management.
# ABOUTME: Handles startup/shutdown for MongoDB, SQLModel and stale streaq cron cleanup.
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from streaq import Worker

from vibetuner.config import settings
from vibetuner.context import Context, ctx
from vibetuner.loader import load_app_config
from vibetuner.logging import logger
from vibetuner.mongo import init_mongodb, teardown_mongodb
from vibetuner.runtime_config import RuntimeConfig
from vibetuner.sqlmodel import init_sqlmodel, teardown_sqlmodel
from vibetuner.tasks.watchdog import LoopWatchdog


LEGACY_HEALTH_CHECK_CRON = "redis_health_check"


async def remove_legacy_health_check_cron(worker: Worker[Any]) -> None:
    """Remove the Redis cron entry left behind by streaq's former built-in health check.

    streaq 6.0-6.2 persisted a `redis_health_check` cron; 6.3 dropped the task but
    not its entry, so every worker start logs "skipped, missing function". Only this
    one name is removed: the same hash holds runtime-scheduled repeating tasks and
    crons from other deploys, which must survive.
    """
    # Drop once streaq removes the entry itself (https://github.com/tastyware/streaq/issues/177)
    # or enough releases have passed that no deployment still carries it.
    if LEGACY_HEALTH_CHECK_CRON in worker.registry:
        return
    if not await worker.redis.hexists(
        worker.cron_registry_key, LEGACY_HEALTH_CHECK_CRON
    ):
        return
    await worker.unschedule_by_id(LEGACY_HEALTH_CHECK_CRON)
    logger.info(
        "Removed orphaned streaq cron entry '{}' left by streaq < 6.3",
        LEGACY_HEALTH_CHECK_CRON,
    )


@asynccontextmanager
async def base_lifespan() -> AsyncGenerator[Context, None]:
    """Base lifespan that initializes core services for the worker."""
    logger.info("Vibetuner task worker starting")

    await init_mongodb()
    await init_sqlmodel()

    if settings.mongodb_url:
        await RuntimeConfig.refresh_cache()
        logger.debug("Runtime config cache initialized")

    watchdog: LoopWatchdog | None = None
    if settings.worker_watchdog_timeout > 0:
        watchdog = LoopWatchdog(
            timeout=settings.worker_watchdog_timeout,
            interval=settings.worker_watchdog_interval,
        )
        watchdog.start()

    yield ctx

    if watchdog is not None:
        await watchdog.stop()

    await teardown_sqlmodel()
    await teardown_mongodb()

    logger.info("Vibetuner task worker stopping")


@asynccontextmanager
async def lifespan() -> AsyncGenerator[Context, None]:
    """Worker lifespan that lazy-loads user's worker_lifespan from tune.py.

    This wrapper prevents circular imports when tune.py imports tasks that
    use @worker.task() or @worker.cron() decorators.
    """
    from vibetuner.tasks.worker import get_worker

    await remove_legacy_health_check_cron(get_worker())

    app_config = load_app_config()
    actual_lifespan = app_config.worker_lifespan or base_lifespan

    async with actual_lifespan() as context:
        yield context
