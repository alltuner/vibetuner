from contextlib import asynccontextmanager

from fastapi import FastAPI

from .context import ctx
from .hotreload import hotreload


@asynccontextmanager
async def lifespan(app: FastAPI):
    if ctx.DEBUG:
        await hotreload.startup()
    # Add below anything that should happen before startup

    # Until here
    yield

    # Add below anything that should happen before shutdown

    # Until here
    if ctx.DEBUG:
        await hotreload.shutdown()
