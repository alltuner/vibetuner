from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from .. import __version__


class AppContext(BaseModel):
    version: str = __version__
    # Add typed state here

    model_config = {"arbitrary_types_allowed": True}


ctx: AppContext = AppContext()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Add below anything that should happen before startup

    yield

    # Add below anything that should happen before shutdown
