from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from vibetuner.context import ctx
from vibetuner.importer import import_module_by_name
from vibetuner.logging import logger
from vibetuner.mongo import init_mongodb, teardown_mongodb
from vibetuner.sqlmodel import init_sqlmodel, teardown_sqlmodel

from .hotreload import hotreload


@asynccontextmanager
async def base_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
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


try:
    lifespan = import_module_by_name("frontend").lifespan
except ModuleNotFoundError:
    logger.warning("No tasks module found; skipping custom task registration.")
    lifespan = base_lifespan
