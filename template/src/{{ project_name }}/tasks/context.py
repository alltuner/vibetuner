from contextlib import asynccontextmanager
from typing import AsyncIterator

from httpx import AsyncClient
from pydantic import BaseModel
from streaq import Worker


class Context(BaseModel):
    http_client: AsyncClient
    # Add the context properties for your tasks below

    # Until here
    model_config = {"arbitrary_types_allowed": True}


@asynccontextmanager
async def lifespan(worker: Worker) -> AsyncIterator[Context]:
    # Add below anything that should happen before startup

    # Until here
    async with (
        AsyncClient() as http_client,
        # Add any other async context managers you need here
    ):
        yield Context(
            http_client=http_client,
            # Add any other async context managers you need here
        )

    # Add below anything that should happen before shutdown
    # Until here
