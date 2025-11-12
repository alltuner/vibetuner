from contextlib import asynccontextmanager

from fastapi import FastAPI

from vibetuner.context import ctx
from vibetuner.logging import logger
from vibetuner.mongo import init_models

from .hotreload import hotreload


@asynccontextmanager
async def base_lifespan(app: FastAPI):
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
except ImportError:
    lifespan = base_lifespan
