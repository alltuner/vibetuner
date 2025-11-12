from contextlib import asynccontextmanager

from fastapi import FastAPI
from vibetuner.config import settings
from vibetuner.frontend.lifespan import base_lifespan
from vibetuner.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.project.project_name} frontend...")

    # Add any startup tasks here

    async with base_lifespan(app):
        yield
        logger.info(f"Stopping {settings.project.project_name} frontend...")

    # Add any teardown tasks here

    logger.info(f"{settings.project.project_name} has shut down.")
