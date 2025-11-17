from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from vibetuner.context import ctx
from vibetuner.logging import logger
from vibetuner.mongo import init_models

from .hotreload import hotreload


@asynccontextmanager
async def base_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Vibetuner frontend starting")
    if ctx.DEBUG:
        await hotreload.startup()

    await init_models()

    yield

    logger.info("Vibetuner frontend stopping")
    if ctx.DEBUG:
        await hotreload.shutdown()
    logger.info("Vibetuner frontend stopped")


try:
    from app.frontend.lifespan import lifespan  # ty: ignore
except ModuleNotFoundError:
    # Silent pass for missing app.frontend.lifespan module (expected in some projects)
    lifespan = base_lifespan
except ImportError as e:
    # Log warning for any import error (including syntax errors, missing dependencies, etc.)
    logger.warning(f"Failed to import app.frontend.lifespan: {e}. Using base lifespan.")
    lifespan = base_lifespan
