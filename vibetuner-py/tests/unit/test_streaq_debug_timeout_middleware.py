# ABOUTME: Unit tests for StreaqDebugTimeoutMiddleware request-level timeout
# ABOUTME: Verifies 504 on hang, pass-through for cheap paths, and non-streaq routes
# ruff: noqa: S101

import asyncio
import time

import pytest
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient
from starlette.types import ASGIApp, Receive, Scope, Send


# Test copy of the middleware to avoid importing the full vibetuner.frontend
# package (which pulls in MongoDB, Redis, OAuth, etc.). Mirrors the
# implementation in vibetuner.frontend.middleware.StreaqDebugTimeoutMiddleware.
STREAQ_DEBUG_REQUEST_TIMEOUT_SECONDS = 5

_STREAQ_DEBUG_SLOW_PREFIXES = (
    "/debug/tasks/queue",
    "/debug/tasks/workers",
)

_STREAQ_DEBUG_TIMEOUT_BODY = (
    b'<!doctype html>'
    b'<html lang="en"><head><meta charset="utf-8">'
    b'<title>504 Gateway Timeout</title></head><body>'
    b'<h1>Task queue view timed out</h1>'
    b'<p>The Streaq debug page took longer than '
    b'5 seconds to load and was cancelled. This usually means the '
    b'underlying Redis SCAN is slow &mdash; see project settings.</p>'
    b'</body></html>'
)


class StreaqDebugTimeoutMiddleware:
    def __init__(self, app: ASGIApp, timeout: float = STREAQ_DEBUG_REQUEST_TIMEOUT_SECONDS):
        self.app = app
        self.timeout = timeout

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if not any(path.startswith(p) for p in _STREAQ_DEBUG_SLOW_PREFIXES):
            await self.app(scope, receive, send)
            return

        response_started = False

        async def send_tracking(message: dict) -> None:
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await asyncio.wait_for(
                self.app(scope, receive, send_tracking), timeout=self.timeout
            )
        except asyncio.TimeoutError:
            if response_started:
                return
            await send(
                {
                    "type": "http.response.start",
                    "status": 504,
                    "headers": [
                        (b"content-type", b"text/html; charset=utf-8"),
                        (
                            b"content-length",
                            str(len(_STREAQ_DEBUG_TIMEOUT_BODY)).encode("ascii"),
                        ),
                    ],
                }
            )
            await send(
                {"type": "http.response.body", "body": _STREAQ_DEBUG_TIMEOUT_BODY}
            )


def _make_app(*, fast: bool, timeout: float = 5.0):
    """Wrap a Starlette inner app with StreaqDebugTimeoutMiddleware.

    The inner app hangs for 10s when `fast=False`, mimicking a stuck Redis
    SCAN. When `fast=True`, it returns immediately so cheap paths can be
    exercised.
    """

    async def hang(request):
        await asyncio.sleep(10)
        return PlainTextResponse("never")  # pragma: no cover

    async def quick(request):
        return PlainTextResponse("OK")

    handler = quick if fast else hang
    inner = Starlette(
        routes=[
            Route("/debug/tasks/queue", handler),
            Route("/debug/tasks/workers", handler),
            Route("/debug/tasks/cron", handler),
            Route("/debug/tasks/", handler),
            Route("/health/live", quick),
        ]
    )
    return StreaqDebugTimeoutMiddleware(inner, timeout=timeout)


class TestStreaqDebugTimeoutMiddleware:
    def test_hang_on_queue_returns_504_within_timeout(self):
        """A hung /debug/tasks/queue request is cancelled and returns 504."""
        app = _make_app(fast=False, timeout=1.0)
        client = TestClient(app)
        start = time.monotonic()
        resp = client.get("/debug/tasks/queue")
        elapsed = time.monotonic() - start

        assert resp.status_code == 504
        assert "text/html" in resp.headers["content-type"]
        assert b"Task queue view timed out" in resp.content
        assert b"Redis SCAN" in resp.content
        # Allow generous slack but well below the 10s inner hang.
        assert elapsed < 3.0, f"Timeout did not fire in time (elapsed={elapsed:.2f}s)"

    def test_hang_on_workers_returns_504(self):
        """A hung /debug/tasks/workers request is cancelled and returns 504."""
        app = _make_app(fast=False, timeout=1.0)
        client = TestClient(app)
        resp = client.get("/debug/tasks/workers")
        assert resp.status_code == 504
        assert b"Task queue view timed out" in resp.content

    def test_cron_path_is_not_guarded(self):
        """/debug/tasks/cron passes through unchanged (not a slow path)."""
        app = _make_app(fast=True, timeout=1.0)
        client = TestClient(app)
        resp = client.get("/debug/tasks/cron")
        assert resp.status_code == 200
        assert resp.text == "OK"

    def test_non_streaq_path_passes_through(self):
        """Paths outside /debug/tasks/queue|workers are not affected."""
        app = _make_app(fast=True, timeout=1.0)
        client = TestClient(app)
        resp = client.get("/health/live")
        assert resp.status_code == 200
        assert resp.text == "OK"

    def test_fast_streaq_request_passes_through(self):
        """A fast /debug/tasks/queue request returns the original response."""
        app = _make_app(fast=True, timeout=1.0)
        client = TestClient(app)
        resp = client.get("/debug/tasks/queue")
        assert resp.status_code == 200
        assert resp.text == "OK"


@pytest.mark.asyncio
async def test_lifespan_passes_through():
    """Non-http scopes (e.g. lifespan) are forwarded without modification."""
    called: list[str] = []

    async def inner_app(scope: Scope, receive: Receive, send: Send) -> None:
        called.append(scope["type"])

    mw = StreaqDebugTimeoutMiddleware(inner_app)

    async def noop_receive() -> dict:  # pragma: no cover - never invoked
        return {"type": "lifespan.startup"}

    async def noop_send(message: dict) -> None:  # pragma: no cover - never invoked
        return

    await mw({"type": "lifespan"}, noop_receive, noop_send)
    assert called == ["lifespan"]
