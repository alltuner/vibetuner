from contextlib import asynccontextmanager
from typing import AsyncIterator

from pydantic import BaseModel
from streaq import Worker


class Context(BaseModel):
    # Add the context properties for your tasks below

    # Until here
    model_config = {"arbitrary_types_allowed": True}


@asynccontextmanager
async def lifespan(worker: Worker) -> AsyncIterator[Context]:
    # Add below anything that should happen before startup
    # Until here
    yield Context(
        # Add your context initialization here
    )

    # Add below anything that should happen before shutdown
    # Until here
