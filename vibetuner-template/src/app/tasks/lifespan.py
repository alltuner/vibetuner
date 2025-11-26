from contextlib import asynccontextmanager
from typing import AsyncGenerator

from vibetuner.context import Context as BaseContext
from vibetuner.logging import logger
from vibetuner.tasks.lifespan import base_lifespan

from ..config import settings


class Context(BaseContext):
    model_config = {"arbitrary_types_allowed": True}


@asynccontextmanager
async def lifespan() -> AsyncGenerator[Context, None]:
    logger.info(f"Starting {settings.project.project_name} task worker...")

    # Tasks here are run before anything is available (even before DB access)
    async with (
        base_lifespan() as worker_ctx,
    ):
        # Tasks here are run after DB is available
        ctx = Context(**worker_ctx.model_dump())

        yield ctx
        # Tasks here are run on shutdown before vibetuner teardown
        logger.info(f"Stopping {settings.project.project_name} task worker...")

    # Add any teardown tasks here

    logger.info(f"{settings.project.project_name} task worker has shut down.")
