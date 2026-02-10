# ABOUTME: Frontend application lifespan management.
# ABOUTME: Handles startup/shutdown for MongoDB, SQLModel, and user customizations.
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from vibetuner.context import ctx
from vibetuner.logging import logger
from vibetuner.mongo import init_mongodb, teardown_mongodb
from vibetuner.sqlmodel import init_sqlmodel, teardown_sqlmodel

from .hotreload import hotreload


@asynccontextmanager
async def base_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Base lifespan that initializes core services."""
    logger.info("Vibetuner frontend starting")
    if ctx.DEBUG:
        await hotreload.startup()

    await init_mongodb()
    await init_sqlmodel()

    # Initialize runtime config cache after MongoDB is ready
    from vibetuner.config import settings
    from vibetuner.runtime_config import RuntimeConfig

    if settings.mongodb_url:
        await RuntimeConfig.refresh_cache()
        logger.debug("Runtime config cache initialized")

    # Initialize worker's Redis connection for task enqueuing from routes
    if settings.workers_available:
        from vibetuner.tasks.worker import get_worker

        async with get_worker():
            yield
    else:
        yield

    logger.info("Vibetuner frontend stopping")
    if ctx.DEBUG:
        await hotreload.shutdown()
    logger.info("Vibetuner frontend stopped")

    await teardown_sqlmodel()
    await teardown_mongodb()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Frontend lifespan that lazy-loads user's frontend_lifespan from tune.py.

    This wrapper prevents circular imports when tune.py imports vibetuner.frontend
    modules that depend on base_lifespan.
    """
    from vibetuner.loader import load_app_config

    app_config = load_app_config()
    actual_lifespan = app_config.frontend_lifespan or base_lifespan

    async with actual_lifespan(app):
        yield
