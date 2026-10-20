# ABOUTME: In-memory pub/sub that fans a reload signal out to connected browsers.
# ABOUTME: Vendored from arel (MIT, see LICENSE in this directory).
import asyncio
from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager


class Notify:
    """Broadcasts a reload signal to every current subscriber."""

    def __init__(self) -> None:
        self._subscriptions: set[asyncio.Queue[str | None]] = set()

    async def notify(self) -> None:
        for queue in self._subscriptions:
            await queue.put("reload")

    async def watch(self) -> AsyncIterator[None]:
        """Yield once per reload signal, until the subscription is closed."""
        async with self._subscribe() as queue:
            while True:
                event = await queue.get()
                if event is None:
                    return
                yield

    @asynccontextmanager
    async def _subscribe(self) -> AsyncGenerator[asyncio.Queue[str | None], None]:
        queue: asyncio.Queue[str | None] = asyncio.Queue()
        self._subscriptions.add(queue)
        try:
            yield queue
        finally:
            self._subscriptions.remove(queue)
            # Unblocks a watcher still waiting on this queue.
            await queue.put(None)
