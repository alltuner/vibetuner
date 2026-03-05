# ABOUTME: Unit tests for vibetuner rate limiting module
# ABOUTME: Tests limiter construction, middleware integration, and decorator behavior
# ruff: noqa: S101

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIASGIMiddleware
from slowapi.util import get_remote_address
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient


def _make_app(limiter: Limiter | None = None, default_limits: list[str] | None = None):
    """Create a minimal Starlette app with rate limiting wired up."""
    if limiter is None:
        limiter = Limiter(
            key_func=get_remote_address,
            storage_uri="memory://",
            default_limits=default_limits or [],
            strategy="fixed-window",
            headers_enabled=True,
            config_filename=None,
        )

    async def homepage(request: Request):
        return PlainTextResponse("OK")

    @limiter.limit("3/minute")
    async def limited_route(request: Request):
        return PlainTextResponse("limited")

    @limiter.limit("1/minute")
    async def strict_route(request: Request):
        return PlainTextResponse("strict")

    @limiter.exempt
    async def exempt_route(request: Request):
        return PlainTextResponse("exempt")

    app = Starlette(
        routes=[
            Route("/", homepage),
            Route("/limited", limited_route),
            Route("/strict", strict_route),
            Route("/exempt", exempt_route),
        ],
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIASGIMiddleware)
    return app


class TestRateLimitDecorator:
    """Test per-route rate limiting with @limiter.limit decorator."""

    def test_under_limit_returns_200(self):
        app = _make_app()
        client = TestClient(app)
        resp = client.get("/limited")
        assert resp.status_code == 200
        assert resp.text == "limited"

    def test_exceeding_limit_returns_429(self):
        app = _make_app()
        client = TestClient(app)
        for _ in range(3):
            resp = client.get("/limited")
            assert resp.status_code == 200
        resp = client.get("/limited")
        assert resp.status_code == 429

    def test_different_routes_have_separate_limits(self):
        app = _make_app()
        client = TestClient(app)
        # Hit strict route limit (1/min)
        resp = client.get("/strict")
        assert resp.status_code == 200
        resp = client.get("/strict")
        assert resp.status_code == 429
        # Limited route should still work
        resp = client.get("/limited")
        assert resp.status_code == 200

    def test_exempt_route_is_not_limited(self):
        app = _make_app(default_limits=["1/minute"])
        client = TestClient(app)
        for _ in range(5):
            resp = client.get("/exempt")
            assert resp.status_code == 200


class TestRateLimitHeaders:
    """Test rate limit response headers."""

    def test_rate_limit_headers_present(self):
        app = _make_app()
        client = TestClient(app)
        resp = client.get("/limited")
        assert "X-RateLimit-Limit" in resp.headers
        assert "X-RateLimit-Remaining" in resp.headers
        assert "X-RateLimit-Reset" in resp.headers

    def test_remaining_decreases(self):
        app = _make_app()
        client = TestClient(app)
        resp1 = client.get("/limited")
        resp2 = client.get("/limited")
        remaining1 = int(resp1.headers["X-RateLimit-Remaining"])
        remaining2 = int(resp2.headers["X-RateLimit-Remaining"])
        assert remaining2 < remaining1

    def test_429_response_has_retry_after(self):
        app = _make_app()
        client = TestClient(app)
        for _ in range(3):
            client.get("/limited")
        resp = client.get("/limited")
        assert resp.status_code == 429
        assert "Retry-After" in resp.headers


class TestDefaultLimits:
    """Test global default rate limits."""

    def test_default_limits_apply_to_undecorated_routes(self):
        app = _make_app(default_limits=["2/minute"])
        client = TestClient(app)
        for _ in range(2):
            resp = client.get("/")
            assert resp.status_code == 200
        resp = client.get("/")
        assert resp.status_code == 429

    def test_decorated_route_overrides_default(self):
        app = _make_app(default_limits=["1/minute"])
        client = TestClient(app)
        # /limited has 3/minute, should override the 1/minute default
        resp = client.get("/limited")
        assert resp.status_code == 200
        resp = client.get("/limited")
        assert resp.status_code == 200


class TestRateLimitConfig:
    """Test rate limit configuration from vibetuner settings."""

    def test_settings_defaults(self):
        from vibetuner.config import RateLimitSettings

        s = RateLimitSettings()
        assert s.enabled is True
        assert s.default_limits == []
        assert s.headers_enabled is True
        assert s.strategy == "fixed-window"
        assert s.swallow_errors is True

    def test_settings_custom_values(self):
        from vibetuner.config import RateLimitSettings

        s = RateLimitSettings(
            enabled=False,
            default_limits=["100/hour"],
            headers_enabled=False,
            strategy="moving-window",
            swallow_errors=False,
        )
        assert s.enabled is False
        assert s.default_limits == ["100/hour"]
        assert s.headers_enabled is False
        assert s.strategy == "moving-window"
        assert s.swallow_errors is False


class TestLimiterConstruction:
    """Test that the vibetuner limiter is properly constructed."""

    def test_limiter_is_importable(self):
        from vibetuner.ratelimit import limiter

        assert isinstance(limiter, Limiter)

    def test_limiter_is_enabled_by_default(self):
        from vibetuner.ratelimit import limiter

        assert limiter.enabled is True
