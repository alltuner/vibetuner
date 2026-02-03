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


# Use user's worker_lifespan from tune.py if provided, otherwise use base
_app_config = load_app_config()
lifespan = _app_config.worker_lifespan or base_lifespan
