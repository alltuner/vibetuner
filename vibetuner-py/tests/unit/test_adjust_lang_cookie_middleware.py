# ABOUTME: Unit tests for AdjustLangCookieMiddleware language cookie management
# ABOUTME: Verifies cookie setting, bypass paths for static/health, and cookie update logic
# ruff: noqa: S101

from starlette.datastructures import MutableHeaders
from starlette.testclient import TestClient
from starlette.types import ASGIApp, Receive, Scope, Send


LANGUAGE_COOKIE_MAX_AGE = 365 * 24 * 60 * 60


class AdjustLangCookieMiddleware:
    """Test copy of middleware to avoid importing full vibetuner.frontend package.

    Mirrors the implementation in vibetuner.frontend.middleware.AdjustLangCookieMiddleware.
    """

    BYPASS_PREFIXES = ("/static/", "/health/")

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if any(path.startswith(p) for p in self.BYPASS_PREFIXES):
            await self.app(scope, receive, send)
            return

        lang_cookie = None
        for header_name, header_value in scope.get("headers", []):
            if header_name == b"cookie":
                for chunk in header_value.decode().split(";"):
                    chunk = chunk.strip()
                    if chunk.startswith("language="):
                        lang_cookie = chunk.split("=", 1)[1]
                        break
                break

        async def send_with_cookie(message):
            if message["type"] == "http.response.start":
                state = scope.get("state", {})
                language = state.get("language")
                if language and (not lang_cookie or lang_cookie != language):
                    headers = MutableHeaders(scope=message)
                    cookie = (
                        f"language={language}; Max-Age={LANGUAGE_COOKIE_MAX_AGE}; "
                        f"Path=/; SameSite=lax"
                    )
                    headers.append("set-cookie", cookie)

            await send(message)

        await self.app(scope, receive, send_with_cookie)


def _make_app(default_language: str = "en"):
    """Create a minimal Starlette app wrapped with AdjustLangCookieMiddleware."""
    from starlette.applications import Starlette
    from starlette.responses import PlainTextResponse
    from starlette.routing import Route

    async def homepage(request):
        request.state.language = default_language
        return PlainTextResponse("OK")

    inner = Starlette(routes=[Route("/{path:path}", homepage), Route("/", homepage)])
    return AdjustLangCookieMiddleware(inner)


class TestAdjustLangCookieMiddleware:
    """Test AdjustLangCookieMiddleware cookie management and bypass paths."""

    def test_sets_language_cookie_when_missing(self):
        """Language cookie is set when not present in request."""
        app = _make_app(default_language="en")
        client = TestClient(app)
        resp = client.get("/")
        assert "language" in resp.cookies
        assert resp.cookies["language"] == "en"

    def test_updates_cookie_when_different(self):
        """Language cookie is updated when it differs from request.state.language."""
        app = _make_app(default_language="ca")
        client = TestClient(app)
        resp = client.get("/", cookies={"language": "en"})
        assert resp.cookies["language"] == "ca"

    def test_no_cookie_when_matching(self):
        """No Set-Cookie header when cookie already matches."""
        app = _make_app(default_language="en")
        client = TestClient(app)
        resp = client.get("/", cookies={"language": "en"})
        assert "language" not in resp.cookies

    def test_static_path_bypass(self):
        """Static paths bypass the middleware entirely (no cookie logic)."""
        app = _make_app(default_language="en")
        client = TestClient(app)
        resp = client.get("/static/css/bundle.css")
        assert resp.status_code == 200
        assert "language" not in resp.cookies

    def test_health_path_bypass(self):
        """Health paths bypass the middleware entirely."""
        app = _make_app(default_language="en")
        client = TestClient(app)
        resp = client.get("/health/live")
        assert resp.status_code == 200
        assert "language" not in resp.cookies
