from contextlib import asynccontextmanager
from typing import AsyncGenerator

from vibetuner.context import Context, ctx
from vibetuner.logging import logger
from vibetuner.mongo import init_models


@asynccontextmanager
async def base_lifespan() -> AsyncGenerator[Context, None]:
    logger.info("Vibetuner task worker starting")

    await init_models()

    yield ctx

    logger.info("Vibetuner task worker stopping")


try:
    from app.tasks.lifespan import lifespan  # ty: ignore
except ModuleNotFoundError:
    # Silent pass for missing app.tasks.lifespan module (expected in some projects)
    lifespan = base_lifespan
except ImportError as e:
    # Log warning for any import error (including syntax errors, missing dependencies, etc.)
    logger.warning(f"Failed to import app.tasks.lifespan: {e}. Using base lifespan.")
    lifespan = base_lifespan
