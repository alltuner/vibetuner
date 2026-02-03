# ABOUTME: Frontend application lifespan management.
# ABOUTME: Handles startup/shutdown for MongoDB, SQLModel, and user customizations.
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from vibetuner.context import ctx
from vibetuner.loader import load_app_config
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

    yield

    logger.info("Vibetuner frontend stopping")
    if ctx.DEBUG:
        await hotreload.shutdown()
    logger.info("Vibetuner frontend stopped")

    await teardown_sqlmodel()
    await teardown_mongodb()


# Use user's frontend_lifespan from tune.py if provided, otherwise use base
_app_config = load_app_config()
lifespan = _app_config.frontend_lifespan or base_lifespan
