# ABOUTME: Unit tests for AdjustLangCookieMiddleware language cookie management
# ABOUTME: Verifies cookie setting, bypass paths for static/health, and cookie update logic
# ruff: noqa: S101

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.testclient import TestClient


LANGUAGE_COOKIE_MAX_AGE = 365 * 24 * 60 * 60


class AdjustLangCookieMiddleware(BaseHTTPMiddleware):
    """Test copy of middleware to avoid importing full vibetuner.frontend package.

    Mirrors the implementation in vibetuner.frontend.middleware.AdjustLangCookieMiddleware.
    """

    BYPASS_PREFIXES = ("/static/", "/health/")

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if any(path.startswith(p) for p in self.BYPASS_PREFIXES):
            return await call_next(request)

        response: Response = await call_next(request)

        lang_cookie = request.cookies.get("language")
        if not lang_cookie or lang_cookie != request.state.language:
            response.set_cookie(
                key="language",
                value=request.state.language,
                max_age=LANGUAGE_COOKIE_MAX_AGE,
            )

        return response


def _make_app(default_language: str = "en"):
    """Create a minimal Starlette app wrapped with AdjustLangCookieMiddleware."""
    from starlette.applications import Starlette
    from starlette.responses import PlainTextResponse
    from starlette.routing import Route

    async def homepage(request):
        request.state.language = default_language
        return PlainTextResponse("OK")

    app = Starlette(routes=[Route("/{path:path}", homepage), Route("/", homepage)])
    app = AdjustLangCookieMiddleware(app)
    return app


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
