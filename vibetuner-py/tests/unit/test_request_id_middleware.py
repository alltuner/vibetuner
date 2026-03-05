# ABOUTME: Unit tests for request ID / correlation ID middleware
# ABOUTME: Verifies X-Request-ID generation, propagation, and Loguru integration
# ruff: noqa: S101

import uuid

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient
from starlette_context import context
from starlette_context.header_keys import HeaderKeys
from starlette_context.middleware import RawContextMiddleware
from starlette_context.plugins import RequestIdPlugin


def _make_app():
    """Create a minimal app with RawContextMiddleware + RequestIdPlugin."""
    captured: dict[str, list] = {"ids": [], "context_ids": []}

    async def homepage(request):
        # Capture request ID from starlette-context
        rid = context.get(HeaderKeys.request_id, "")
        captured["ids"].append(rid)
        return PlainTextResponse("OK")

    app = Starlette(routes=[Route("/", homepage), Route("/{path:path}", homepage)])
    app = RawContextMiddleware(app, plugins=[RequestIdPlugin(validate=False)])
    app._captured = captured  # type: ignore[attr-defined]
    return app


class TestRequestIdMiddleware:
    """Test X-Request-ID generation and propagation."""

    def test_generates_request_id_when_missing(self):
        """A new UUID is generated when no X-Request-ID header is sent."""
        app = _make_app()
        client = TestClient(app)
        resp = client.get("/")
        assert resp.status_code == 200
        assert "X-Request-ID" in resp.headers
        # Should be a valid UUID
        rid = resp.headers["X-Request-ID"]
        uuid.UUID(rid)  # raises if invalid

    def test_propagates_incoming_request_id(self):
        """An incoming X-Request-ID is reused in the response."""
        app = _make_app()
        client = TestClient(app)
        custom_id = "my-trace-id-12345"
        resp = client.get("/", headers={"X-Request-ID": custom_id})
        assert resp.headers["X-Request-ID"] == custom_id

    def test_request_id_available_in_context(self):
        """The request ID is accessible via starlette_context.context inside handlers."""
        app = _make_app()
        client = TestClient(app)
        custom_id = "ctx-test-id"
        client.get("/", headers={"X-Request-ID": custom_id})
        assert app._captured["ids"] == [custom_id]

    def test_different_requests_get_different_ids(self):
        """Two requests without X-Request-ID get distinct generated IDs."""
        app = _make_app()
        client = TestClient(app)
        resp1 = client.get("/")
        resp2 = client.get("/")
        assert resp1.headers["X-Request-ID"] != resp2.headers["X-Request-ID"]

    def test_response_header_present_on_all_status_codes(self):
        """X-Request-ID is returned even on error responses."""
        async def error_handler(request):
            return PlainTextResponse("Not Found", status_code=404)

        error_app = Starlette(routes=[Route("/", error_handler)])
        error_app = RawContextMiddleware(error_app, plugins=[RequestIdPlugin()])
        client = TestClient(error_app)
        resp = client.get("/")
        assert resp.status_code == 404
        assert "X-Request-ID" in resp.headers


class TestRequestIdLoguruIntegration:
    """Test that request ID is injected into Loguru log records."""

    def test_patcher_injects_request_id(self):
        """The _request_id_patcher populates extra['request_id'] from context."""
        from vibetuner.logging import _request_id_patcher

        # Outside request context — should default to empty string
        record = {"extra": {}}
        _request_id_patcher(record)
        assert record["extra"]["request_id"] == ""

    def test_patcher_reads_from_context(self):
        """The patcher reads request_id from starlette-context when available."""
        from starlette_context import _request_scope_context_storage
        from vibetuner.logging import _request_id_patcher

        # Simulate an active request context
        token = _request_scope_context_storage.set({HeaderKeys.request_id: "test-rid"})
        try:
            record = {"extra": {}}
            _request_id_patcher(record)
            assert record["extra"]["request_id"] == "test-rid"
        finally:
            _request_scope_context_storage.reset(token)
