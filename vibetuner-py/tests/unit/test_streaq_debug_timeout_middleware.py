# ABOUTME: Unit tests for StreaqDebugTimeoutMiddleware request-level timeout
# ABOUTME: Verifies HTML fallback on hang, JSON for API clients, and pass-through paths
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
# implementation in vibetuner.frontend.middleware.StreaqDebugTimeoutMiddleware,
# including the HTML/JSON content negotiation and the inline fallback used when
# the project's template engine is unavailable.
STREAQ_DEBUG_REQUEST_TIMEOUT_SECONDS = 5

_STREAQ_DEBUG_SLOW_PREFIXES = (
    "/debug/tasks/queue",
    "/debug/tasks/workers",
)

_STREAQ_DEBUG_TIMEOUT_JSON = (
    b'{"error":"streaq_debug_timeout",'
    b'"detail":"Streaq debug UI did not respond within '
    + str(STREAQ_DEBUG_REQUEST_TIMEOUT_SECONDS).encode("ascii")
    + b"s. Check that the worker is running, Redis is reachable, "
    b'and the installed streaq version is compatible."}'
)

_STREAQ_DEBUG_TIMEOUT_HTML = (
    b'<!doctype html><html lang="en"><head><meta charset="utf-8">'
    b"<title>504 Gateway Timeout</title></head><body>"
    b"<h1>Task queue unavailable</h1>"
    b"<p>The Streaq debug UI did not respond in time. "
    b"Check that the worker is running, Redis is reachable, "
    b"and the installed streaq version is compatible.</p>"
    b"</body></html>"
)


def _wants_html(scope: Scope) -> bool:
    for header_name, header_value in scope.get("headers", []):
        if header_name == b"accept":
            accept = header_value.decode("latin-1", errors="replace").lower()
            if "application/json" in accept and "text/html" not in accept:
                return False
            return True
    return True


class StreaqDebugTimeoutMiddleware:
    def __init__(
        self, app: ASGIApp, timeout: float = STREAQ_DEBUG_REQUEST_TIMEOUT_SECONDS
    ):
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
            if _wants_html(scope):
                body = _STREAQ_DEBUG_TIMEOUT_HTML
                content_type = b"text/html; charset=utf-8"
            else:
                body = _STREAQ_DEBUG_TIMEOUT_JSON
                content_type = b"application/json"
            await send(
                {
                    "type": "http.response.start",
                    "status": 504,
                    "headers": [
                        (b"content-type", content_type),
                        (b"content-length", str(len(body)).encode("ascii")),
                    ],
                }
            )
            await send({"type": "http.response.body", "body": body})


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
    def test_hang_on_queue_returns_html_within_timeout(self):
        """A hung /debug/tasks/queue request is cancelled and returns the HTML fallback."""
        app = _make_app(fast=False, timeout=1.0)
        client = TestClient(app)
        start = time.monotonic()
        resp = client.get("/debug/tasks/queue")
        elapsed = time.monotonic() - start

        assert resp.status_code == 504
        assert "text/html" in resp.headers["content-type"]
        assert b"Task queue unavailable" in resp.content
        assert b"worker is running" in resp.content
        # Allow generous slack but well below the 10s inner hang.
        assert elapsed < 3.0, f"Timeout did not fire in time (elapsed={elapsed:.2f}s)"

    def test_hang_on_workers_returns_html(self):
        """A hung /debug/tasks/workers request is cancelled and returns the HTML fallback."""
        app = _make_app(fast=False, timeout=1.0)
        client = TestClient(app)
        resp = client.get("/debug/tasks/workers")
        assert resp.status_code == 504
        assert b"Task queue unavailable" in resp.content

    def test_json_client_gets_json_payload(self):
        """Accept: application/json gets structured JSON instead of HTML."""
        app = _make_app(fast=False, timeout=1.0)
        client = TestClient(app)
        resp = client.get("/debug/tasks/queue", headers={"accept": "application/json"})
        assert resp.status_code == 504
        assert "application/json" in resp.headers["content-type"]
        assert resp.json()["error"] == "streaq_debug_timeout"
        assert "worker is running" in resp.json()["detail"]

    def test_browser_accept_header_still_returns_html(self):
        """A browser Accept header that also lists JSON still gets HTML."""
        app = _make_app(fast=False, timeout=1.0)
        client = TestClient(app)
        resp = client.get(
            "/debug/tasks/queue",
            headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            },
        )
        assert resp.status_code == 504
        assert "text/html" in resp.headers["content-type"]

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


class TestStreaqDebugTimeoutMiddlewareRealRendering:
    """Verifies the production middleware drives the Jinja template path.

    We do not render the skeleton-extending template end-to-end here because
    the skeleton has named-route dependencies (`url_for("css")`, etc.) that
    only exist inside the full FastAPI app. Instead, we patch render_template
    to confirm the middleware reaches it with the expected arguments, and
    rely on the inline HTML fallback for the bytes-on-wire assertions.
    """

    def test_real_middleware_invokes_render_template(self, monkeypatch):
        """Hung request invokes render_template with the fallback template."""
        from starlette.responses import HTMLResponse
        from vibetuner.frontend import middleware as mw_mod

        captured: dict = {}

        def fake_render(template, request, ctx, **kwargs):
            captured["template"] = template
            captured["ctx"] = ctx
            captured["status_code"] = kwargs.get("status_code")
            return HTMLResponse(b"<html>rendered</html>", status_code=504)

        monkeypatch.setattr("vibetuner.rendering.render_template", fake_render)
        monkeypatch.setattr(mw_mod, "STREAQ_DEBUG_REQUEST_TIMEOUT_SECONDS", 1)

        async def hang(request):
            await asyncio.sleep(10)
            return PlainTextResponse("never")  # pragma: no cover

        inner = Starlette(routes=[Route("/debug/tasks/queue", hang)])
        app = mw_mod.StreaqDebugTimeoutMiddleware(inner)
        client = TestClient(app)
        resp = client.get("/debug/tasks/queue")

        assert resp.status_code == 504
        assert resp.content == b"<html>rendered</html>"
        assert captured["template"] == "debug/tasks_unavailable.html.jinja"
        assert captured["ctx"]["path"] == "/debug/tasks/queue"
        assert captured["ctx"]["timeout_seconds"] == 1
        assert captured["status_code"] == 504

    def test_real_middleware_json_path(self, monkeypatch):
        """API clients still get JSON from the real middleware."""
        from vibetuner.frontend import middleware as mw_mod

        monkeypatch.setattr(mw_mod, "STREAQ_DEBUG_REQUEST_TIMEOUT_SECONDS", 1)

        async def hang(request):
            await asyncio.sleep(10)
            return PlainTextResponse("never")  # pragma: no cover

        inner = Starlette(routes=[Route("/debug/tasks/queue", hang)])
        app = mw_mod.StreaqDebugTimeoutMiddleware(inner)
        client = TestClient(app)
        resp = client.get("/debug/tasks/queue", headers={"accept": "application/json"})

        assert resp.status_code == 504
        assert "application/json" in resp.headers["content-type"]
        assert resp.json()["error"] == "streaq_debug_timeout"
