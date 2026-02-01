from contextlib import asynccontextmanager
from typing import AsyncGenerator

from vibetuner.context import Context, ctx
from vibetuner.importer import import_module_by_name
from vibetuner.logging import logger
from vibetuner.mongo import init_mongodb, teardown_mongodb
from vibetuner.sqlmodel import init_sqlmodel, teardown_sqlmodel


@asynccontextmanager
async def base_lifespan() -> AsyncGenerator[Context, None]:
    logger.info("Vibetuner task worker starting")

    await init_mongodb()
    await init_sqlmodel()

    yield ctx

    await teardown_sqlmodel()
    await teardown_mongodb()

    logger.info("Vibetuner task worker stopping")


try:
    lifespan = import_module_by_name("tasks").lifespan
except (ModuleNotFoundError, AttributeError):
    logger.warning("No tasks lifespan found; using base lifespan.")
    lifespan = base_lifespan
