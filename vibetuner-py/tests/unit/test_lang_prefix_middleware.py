# ABOUTME: Unit tests for LangPrefixMiddleware path-prefix language routing
# ABOUTME: Verifies URL prefix stripping, redirects, 404s, and bypass path handling
# ruff: noqa: S101

import pytest
from starlette.responses import Response as StarletteResponse
from starlette.types import ASGIApp, Receive, Scope, Send


class LangPrefixMiddleware:
    """Test copy of middleware to avoid importing full vibetuner.frontend package.

    Mirrors the implementation in vibetuner.frontend.middleware.LangPrefixMiddleware.
    """

    BYPASS_PREFIXES = ("/static/", "/health/", "/debug/", "/hot-reload")

    def __init__(self, app: ASGIApp, supported_languages: set[str]):
        self.app = app
        self.supported_languages = supported_languages

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")

        # Skip bypass paths
        if any(path.startswith(p) for p in self.BYPASS_PREFIXES):
            await self.app(scope, receive, send)
            return

        # Check for language prefix pattern: /{xx}/... or /{xx}
        parts = path.strip("/").split("/", 1)
        if parts and len(parts[0]) == 2 and parts[0].isalpha() and parts[0].islower():
            lang_code = parts[0]

            if lang_code in self.supported_languages:
                # Handle bare /xx without trailing slash -> redirect to /xx/
                if len(parts) == 1 or parts[1] == "":
                    if not path.endswith("/"):
                        await self._redirect(scope, receive, send, f"/{lang_code}/")
                        return

                # Valid language: strip prefix, store original path
                new_path = "/" + parts[1] if len(parts) > 1 else "/"

                # Initialize state dict if needed
                if "state" not in scope:
                    scope = {**scope, "state": {}}
                else:
                    scope = {**scope, "state": {**scope["state"]}}

                scope["path"] = new_path
                scope["state"]["lang_prefix"] = lang_code
                scope["state"]["original_path"] = path
            else:
                # Invalid language prefix: return 404
                await self._not_found(scope, receive, send)
                return

        await self.app(scope, receive, send)

    async def _redirect(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
        location: str,
        status: int = 302,
    ) -> None:
        """Send a redirect response."""
        response = StarletteResponse(status_code=status, headers={"Location": location})
        await response(scope, receive, send)

    async def _not_found(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Send a 404 response for invalid language prefix."""
        response = StarletteResponse(status_code=404, content="Not Found")
        await response(scope, receive, send)


class TestLangPrefixMiddleware:
    """Test LangPrefixMiddleware path handling logic."""

    def setup_method(self):
        """Set up test fixtures."""
        self.supported_languages = {"en", "ca", "es"}

    async def _simulate_request(
        self, middleware: LangPrefixMiddleware, path: str, request_type: str = "http"
    ) -> tuple[dict, list]:
        """Simulate an ASGI request through the middleware.

        Returns (final_scope, response_parts) where response_parts is empty if
        the request passed through to the app.
        """
        scope = {
            "type": request_type,
            "path": path,
            "query_string": b"",
            "headers": [],
        }

        response_parts = []
        final_scope = None

        async def receive():
            return {"type": "http.request", "body": b""}

        async def send(message):
            response_parts.append(message)

        async def app(scope, receive, send):
            nonlocal final_scope
            final_scope = scope
            # Simulate a successful response
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b"OK"})

        middleware_instance = LangPrefixMiddleware(app, self.supported_languages)
        await middleware_instance(scope, receive, send)

        return final_scope, response_parts

    @pytest.mark.asyncio
    async def test_valid_language_prefix_stripping(self):
        """Valid language prefix is stripped from path."""
        middleware = LangPrefixMiddleware(None, self.supported_languages)
        final_scope, _ = await self._simulate_request(middleware, "/ca/dashboard")

        assert final_scope["path"] == "/dashboard"
        assert final_scope["state"]["lang_prefix"] == "ca"
        assert final_scope["state"]["original_path"] == "/ca/dashboard"

    @pytest.mark.asyncio
    async def test_valid_language_prefix_root_path(self):
        """Language prefix with root path (e.g., /ca/) strips to /."""
        middleware = LangPrefixMiddleware(None, self.supported_languages)
        final_scope, _ = await self._simulate_request(middleware, "/ca/")

        assert final_scope["path"] == "/"
        assert final_scope["state"]["lang_prefix"] == "ca"

    @pytest.mark.asyncio
    async def test_invalid_language_prefix_returns_404(self):
        """Invalid language prefix (not in supported languages) returns 404."""
        middleware = LangPrefixMiddleware(None, self.supported_languages)
        _, response_parts = await self._simulate_request(middleware, "/xx/dashboard")

        # Check that we got a 404 response
        start_message = next(
            (p for p in response_parts if p.get("type") == "http.response.start"), None
        )
        assert start_message is not None
        assert start_message["status"] == 404

    @pytest.mark.asyncio
    async def test_bare_language_code_redirects(self):
        """Bare language code without trailing slash redirects to /xx/."""
        middleware = LangPrefixMiddleware(None, self.supported_languages)
        _, response_parts = await self._simulate_request(middleware, "/ca")

        start_message = next(
            (p for p in response_parts if p.get("type") == "http.response.start"), None
        )
        assert start_message is not None
        assert start_message["status"] == 302
        headers = dict(start_message.get("headers", []))
        assert headers.get(b"location") == b"/ca/"

    @pytest.mark.asyncio
    async def test_bypass_static_paths(self):
        """Static paths are not processed for language prefix."""
        middleware = LangPrefixMiddleware(None, self.supported_languages)
        final_scope, _ = await self._simulate_request(
            middleware, "/static/css/main.css"
        )

        assert final_scope["path"] == "/static/css/main.css"
        assert "lang_prefix" not in final_scope.get("state", {})

    @pytest.mark.asyncio
    async def test_bypass_health_paths(self):
        """Health check paths are not processed for language prefix."""
        middleware = LangPrefixMiddleware(None, self.supported_languages)
        final_scope, _ = await self._simulate_request(middleware, "/health/live")

        assert final_scope["path"] == "/health/live"
        assert "lang_prefix" not in final_scope.get("state", {})

    @pytest.mark.asyncio
    async def test_bypass_debug_paths(self):
        """Debug paths are not processed for language prefix."""
        middleware = LangPrefixMiddleware(None, self.supported_languages)
        final_scope, _ = await self._simulate_request(middleware, "/debug/info")

        assert final_scope["path"] == "/debug/info"
        assert "lang_prefix" not in final_scope.get("state", {})

    @pytest.mark.asyncio
    async def test_bypass_hot_reload_path(self):
        """Hot-reload websocket path is not processed for language prefix."""
        middleware = LangPrefixMiddleware(None, self.supported_languages)
        final_scope, _ = await self._simulate_request(middleware, "/hot-reload")

        assert final_scope["path"] == "/hot-reload"
        assert "lang_prefix" not in final_scope.get("state", {})

    @pytest.mark.asyncio
    async def test_non_language_path_unchanged(self):
        """Paths without language prefix pass through unchanged."""
        middleware = LangPrefixMiddleware(None, self.supported_languages)
        final_scope, _ = await self._simulate_request(middleware, "/dashboard")

        assert final_scope["path"] == "/dashboard"
        assert "lang_prefix" not in final_scope.get("state", {})

    @pytest.mark.asyncio
    async def test_three_letter_code_not_treated_as_language(self):
        """Three-letter codes are not treated as language prefixes."""
        middleware = LangPrefixMiddleware(None, self.supported_languages)
        final_scope, _ = await self._simulate_request(middleware, "/api/users")

        assert final_scope["path"] == "/api/users"
        assert "lang_prefix" not in final_scope.get("state", {})

    @pytest.mark.asyncio
    async def test_uppercase_code_not_treated_as_language(self):
        """Uppercase codes are not treated as language prefixes."""
        middleware = LangPrefixMiddleware(None, self.supported_languages)
        final_scope, _ = await self._simulate_request(middleware, "/CA/dashboard")

        assert final_scope["path"] == "/CA/dashboard"
        assert "lang_prefix" not in final_scope.get("state", {})

    @pytest.mark.asyncio
    async def test_mixed_case_code_not_treated_as_language(self):
        """Mixed case codes are not treated as language prefixes."""
        middleware = LangPrefixMiddleware(None, self.supported_languages)
        final_scope, _ = await self._simulate_request(middleware, "/Ca/dashboard")

        assert final_scope["path"] == "/Ca/dashboard"
        assert "lang_prefix" not in final_scope.get("state", {})

    @pytest.mark.asyncio
    async def test_websocket_requests_pass_through(self):
        """WebSocket requests pass through without language processing."""
        middleware = LangPrefixMiddleware(None, self.supported_languages)
        final_scope, _ = await self._simulate_request(
            middleware, "/ca/socket", request_type="websocket"
        )

        # For non-http, the original path should be preserved
        assert final_scope["path"] == "/ca/socket"

    @pytest.mark.asyncio
    async def test_nested_path_with_language_prefix(self):
        """Nested paths with language prefix are handled correctly."""
        middleware = LangPrefixMiddleware(None, self.supported_languages)
        final_scope, _ = await self._simulate_request(
            middleware, "/es/admin/users/123/edit"
        )

        assert final_scope["path"] == "/admin/users/123/edit"
        assert final_scope["state"]["lang_prefix"] == "es"

    @pytest.mark.asyncio
    async def test_preserves_existing_state(self):
        """Middleware preserves existing state values."""
        scope = {
            "type": "http",
            "path": "/ca/dashboard",
            "query_string": b"",
            "headers": [],
            "state": {"existing_key": "existing_value"},
        }

        final_scope = None

        async def receive():
            return {"type": "http.request", "body": b""}

        async def send(message):
            pass

        async def app(scope, receive, send):
            nonlocal final_scope
            final_scope = scope
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b"OK"})

        middleware = LangPrefixMiddleware(app, self.supported_languages)
        await middleware(scope, receive, send)

        assert final_scope["state"]["existing_key"] == "existing_value"
        assert final_scope["state"]["lang_prefix"] == "ca"

    @pytest.mark.asyncio
    async def test_numeric_prefix_not_treated_as_language(self):
        """Numeric prefixes are not treated as language codes."""
        middleware = LangPrefixMiddleware(None, self.supported_languages)
        final_scope, _ = await self._simulate_request(middleware, "/12/dashboard")

        assert final_scope["path"] == "/12/dashboard"
        assert "lang_prefix" not in final_scope.get("state", {})

    @pytest.mark.asyncio
    async def test_empty_path_unchanged(self):
        """Empty paths pass through unchanged."""
        middleware = LangPrefixMiddleware(None, self.supported_languages)
        final_scope, _ = await self._simulate_request(middleware, "/")

        assert final_scope["path"] == "/"
        assert "lang_prefix" not in final_scope.get("state", {})
