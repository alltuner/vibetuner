# ABOUTME: Dev-only hot reload: a WebSocket endpoint that tells the browser to reload.
# ABOUTME: Vendored from arel (MIT, see LICENSE in this directory).
import functools
import pathlib
import string
from collections.abc import Awaitable, Callable, Sequence
from typing import NamedTuple

import anyio
from starlette.types import Receive, Scope, Send
from starlette.websockets import WebSocket

from vibetuner.logging import logger

from .notify import Notify
from .watcher import ChangeSet, FileWatcher


ReloadFunc = Callable[[], Awaitable[None]]

CLIENT_SCRIPT = pathlib.Path(__file__).parent / "client.js"


class Path(NamedTuple):
    """A watched directory, with optional server-side hooks to run first."""

    path: str
    on_reload: Sequence[ReloadFunc] = ()


class _Template(string.Template):
    delimiter = "$hotreload::"


class HotReload:
    """Watches paths and reloads connected browsers when they change.

    Instances are ASGI applications, mounted as a WebSocket route. The page
    opens that socket through the script ``script()`` renders, and reloads when
    the socket says so or when it reconnects after a server restart.
    """

    def __init__(self, paths: Sequence[Path], reconnect_interval: float = 1.0) -> None:
        self.notify = Notify()
        self.watchers = [
            FileWatcher(
                path,
                on_change=functools.partial(self._on_changes, on_reload=on_reload),
            )
            for path, on_reload in paths
        ]
        self._reconnect_interval = reconnect_interval

    async def _on_changes(
        self, changeset: ChangeSet, *, on_reload: Sequence[ReloadFunc]
    ) -> None:
        description = ", ".join(
            f"{event}: {', '.join(changeset[event])}" for event in changeset
        )
        logger.info("Detected changes ({}); triggering reload", description)

        # Server-side hooks run before the browser is told to reload.
        for callback in on_reload:
            await callback()

        await self.notify.notify()

    def script(self, url: str) -> str:
        """Render the client script that connects back to ``url``."""
        if not hasattr(self, "_script_template"):
            self._script_template = _Template(CLIENT_SCRIPT.read_text())

        content = self._script_template.substitute(
            {"url": url, "reconnect_interval": self._reconnect_interval}
        )
        return f"<script>{content}</script>"

    async def startup(self) -> None:
        for watcher in self.watchers:
            await watcher.startup()

    async def shutdown(self) -> None:
        for watcher in self.watchers:
            await watcher.shutdown()

    async def _wait_client_disconnect(self, ws: WebSocket) -> None:
        async for _ in ws.iter_text():
            pass

    async def _watch_reloads(self, ws: WebSocket) -> None:
        async for _ in self.notify.watch():
            await ws.send_text("reload")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "websocket":
            raise RuntimeError(
                f"Hot reload is a WebSocket route, got {scope['type']!r}"
            )
        ws = WebSocket(scope, receive, send)
        await ws.accept()
        async with anyio.create_task_group() as task_group:

            async def run(func: Callable[[WebSocket], Awaitable[None]]) -> None:
                await func(ws)
                task_group.cancel_scope.cancel()

            task_group.start_soon(run, self._watch_reloads)
            task_group.start_soon(run, self._wait_client_disconnect)
