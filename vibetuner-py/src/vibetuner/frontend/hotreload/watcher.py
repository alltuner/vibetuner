# ABOUTME: Watches a directory for file changes and reports them as a changeset.
# ABOUTME: Vendored from arel (MIT, see LICENSE in this directory).
import asyncio
import itertools
from collections.abc import Awaitable, Callable

import watchfiles

from vibetuner.logging import logger


ChangeSet = dict[str, list[str]]

CHANGE_EVENT_LABELS = {
    watchfiles.Change.added: "added",
    watchfiles.Change.modified: "modified",
    watchfiles.Change.deleted: "deleted",
}


class FileWatcher:
    """Reports changes under ``path`` until shut down."""

    def __init__(
        self, path: str, on_change: Callable[[ChangeSet], Awaitable[None]]
    ) -> None:
        self._path = path
        self._on_change = on_change
        self._task: asyncio.Task[None] | None = None

    @property
    def _should_exit(self) -> asyncio.Event:
        # Created lazily: hot reload may not run in the thread this object was
        # created in, and an Event binds to the loop that first awaits it.
        if not hasattr(self, "_should_exit_obj"):
            self._should_exit_obj = asyncio.Event()
        return self._should_exit_obj

    async def _watch(self) -> None:
        async for changes in watchfiles.awatch(self._path):
            changeset: ChangeSet = {}
            for event, group in itertools.groupby(changes, key=lambda item: item[0]):
                changeset[CHANGE_EVENT_LABELS[event]] = [path for _, path in group]
            await self._on_change(changeset)

    async def _main(self) -> None:
        tasks = [
            asyncio.create_task(self._watch()),
            asyncio.create_task(self._should_exit.wait()),
        ]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
        for task in done:
            task.result()

    async def startup(self) -> None:
        if self._task is not None:
            raise RuntimeError(f"Already watching {self._path!r}")
        self._task = asyncio.create_task(self._main())
        logger.info("Started watching file changes at {!r}", self._path)

    async def shutdown(self) -> None:
        if self._task is None:
            return
        logger.info("Stopping file watching at {!r}", self._path)
        self._should_exit.set()
        await self._task
        self._task = None
