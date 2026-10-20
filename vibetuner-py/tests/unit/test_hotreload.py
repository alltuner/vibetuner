# ABOUTME: Tests for the vendored dev hot reload: client script, WebSocket route, file watcher.
# ABOUTME: It is framework code now, and its WebSocket wiring must track starlette's API.
# ruff: noqa: S101, S603
import asyncio
import subprocess
import sys
import textwrap
from pathlib import Path as FsPath

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.routing import WebSocketRoute
from vibetuner.frontend.hotreload.reloader import HotReload, Path
from vibetuner.frontend.hotreload.watcher import FileWatcher


def _app(hotreload: HotReload) -> FastAPI:
    """Mount hot reload the way vibetuner.frontend.application does."""
    app = FastAPI()
    app.router.routes.append(
        WebSocketRoute("/hot-reload", hotreload, name="hot-reload")
    )
    return app


class TestClientScript:
    def test_renders_url_and_interval(self):
        hotreload = HotReload(paths=[], reconnect_interval=2)

        script = hotreload.script("ws://localhost:8000/hot-reload")

        assert script.startswith("<script>")
        assert 'new WebSocket("ws://localhost:8000/hot-reload")' in script
        assert 'parseFloat("2")' in script

    def test_leaves_no_placeholder_unsubstituted(self):
        script = HotReload(paths=[]).script("ws://example/hot-reload")

        assert "$hotreload::" not in script


class TestWebSocketRoute:
    def test_browser_is_told_to_reload_on_a_change(self):
        hotreload = HotReload(paths=[])
        with TestClient(_app(hotreload)).websocket_connect("/hot-reload") as ws:
            asyncio.run(hotreload.notify.notify())

            assert ws.receive_text() == "reload"

    def test_connection_is_accepted_without_any_change(self):
        hotreload = HotReload(paths=[])
        with TestClient(_app(hotreload)).websocket_connect("/hot-reload") as ws:
            ws.close()

    def test_rejects_a_plain_http_request(self):
        hotreload = HotReload(paths=[])

        with pytest.raises(RuntimeError, match="WebSocket route"):
            asyncio.run(hotreload({"type": "http"}, None, None))


class TestFileWatcher:
    async def test_reports_a_real_file_change(self, tmp_path: FsPath):
        seen: asyncio.Queue[dict[str, list[str]]] = asyncio.Queue()
        watcher = FileWatcher(str(tmp_path), on_change=seen.put)
        watched = tmp_path / "page.html.jinja"
        watched.write_text("before")

        await watcher.startup()
        try:
            # watchfiles polls, so write after startup and allow a few cycles.
            await asyncio.sleep(0.2)
            watched.write_text("after")
            changeset = await asyncio.wait_for(seen.get(), timeout=10)
        finally:
            await watcher.shutdown()

        assert [str(watched) in paths for paths in changeset.values()] == [True]

    async def test_shutdown_is_idempotent(self, tmp_path: FsPath):
        watcher = FileWatcher(str(tmp_path), on_change=lambda _: asyncio.sleep(0))

        await watcher.shutdown()
        await watcher.startup()
        await watcher.shutdown()
        await watcher.shutdown()

    async def test_refuses_to_start_twice(self, tmp_path: FsPath):
        watcher = FileWatcher(str(tmp_path), on_change=lambda _: asyncio.sleep(0))

        await watcher.startup()
        try:
            with pytest.raises(RuntimeError, match="Already watching"):
                await watcher.startup()
        finally:
            await watcher.shutdown()


class TestReloadHooks:
    async def test_server_side_hook_runs_before_the_browser_is_told(self):
        order: list[str] = []

        async def hook() -> None:
            order.append("hook")

        hotreload = HotReload(paths=[Path("unused", on_reload=[hook])])

        async def record() -> None:
            async for _ in hotreload.notify.watch():
                order.append("notified")
                return

        watching = asyncio.create_task(record())
        await asyncio.sleep(0)
        await hotreload._on_changes({"modified": ["x"]}, on_reload=[hook])
        await asyncio.wait_for(watching, timeout=5)

        assert order == ["hook", "notified"]


class TestRealAppWiring:
    """The skeleton template renders ``url_for('hot-reload')``, so the real app
    must register that route under DEBUG or every page render raises."""

    def test_debug_app_registers_a_named_hot_reload_route(self):
        # A fresh interpreter: vibetuner.frontend.application builds the app at
        # import time, and DEBUG has to be set before that happens.
        script = textwrap.dedent(
            """
            import os
            os.environ["DEBUG"] = "true"

            from starlette.routing import WebSocketRoute
            from vibetuner.frontend.application import app

            route = next(
                r for r in app.router.routes
                if getattr(r, "name", None) == "hot-reload"
            )
            assert isinstance(route, WebSocketRoute), type(route)
            assert app.url_path_for("hot-reload") == "/hot-reload"
            print("OK")
            """
        )
        result = subprocess.run(
            [sys.executable, "-c", script], capture_output=True, check=False, text=True
        )
        assert result.returncode == 0, result.stderr
        assert "OK" in result.stdout
