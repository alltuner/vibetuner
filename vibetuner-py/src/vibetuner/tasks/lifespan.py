# ABOUTME: Task worker lifespan management.
# ABOUTME: Handles startup/shutdown for MongoDB, SQLModel in worker context.
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from vibetuner.context import Context, ctx
from vibetuner.loader import load_app_config
from vibetuner.logging import logger
from vibetuner.mongo import init_mongodb, teardown_mongodb
from vibetuner.sqlmodel import init_sqlmodel, teardown_sqlmodel


@asynccontextmanager
async def base_lifespan() -> AsyncGenerator[Context, None]:
    """Base lifespan that initializes core services for the worker."""
    logger.info("Vibetuner task worker starting")

    await init_mongodb()
    await init_sqlmodel()

    yield ctx

    await teardown_sqlmodel()
    await teardown_mongodb()

    logger.info("Vibetuner task worker stopping")


@asynccontextmanager
async def lifespan() -> AsyncGenerator[Context, None]:
    """Worker lifespan that lazy-loads user's worker_lifespan from tune.py.

    This wrapper prevents circular imports when tune.py imports tasks that
    use @worker.task() or @worker.cron() decorators.
    """
    app_config = load_app_config()
    actual_lifespan = app_config.worker_lifespan or base_lifespan

    async with actual_lifespan() as context:
        yield context
