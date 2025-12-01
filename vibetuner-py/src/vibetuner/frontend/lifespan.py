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
    logger.info("Vibetuner frontend starting")
    if ctx.DEBUG:
        await hotreload.startup()

    await init_mongodb()
    await init_sqlmodel()

    yield

    logger.info("Vibetuner frontend stopping")
    if ctx.DEBUG:
        await hotreload.shutdown()
    logger.info("Vibetuner frontend stopped")

    await teardown_sqlmodel()
    await teardown_mongodb()


try:
    from app.frontend.lifespan import lifespan  # ty: ignore
except ModuleNotFoundError:
    # Silent pass for missing app.frontend.lifespan module (expected in some projects)
    lifespan = base_lifespan
except ImportError as e:
    # Log warning for any import error (including syntax errors, missing dependencies, etc.)
    logger.warning(f"Failed to import app.frontend.lifespan: {e}. Using base lifespan.")
    lifespan = base_lifespan
