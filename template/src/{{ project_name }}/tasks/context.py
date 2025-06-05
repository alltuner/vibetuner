from contextlib import asynccontextmanager
from typing import AsyncIterator

from pydantic import BaseModel
from streaq import Worker


class Context(BaseModel):
    """
    Define the dependencies of your tasks.
    """

    model_config = {"arbitrary_types_allowed": True}


@asynccontextmanager
async def lifespan(worker: Worker) -> AsyncIterator[Context]:
    yield Context()

    # async with AsyncClient() as http_client:
    #    yield Context(http_client)
