from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Add below anything that should happen before startup

    yield

    # Add below anything that should happen before shutdown
