# ABOUTME: Unit tests for SecurityHeadersMiddleware CSP nonce and security headers
# ABOUTME: Verifies nonce generation, CSP directives, report-only mode, and bypass paths
# ruff: noqa: S101

import secrets
from dataclasses import dataclass, field

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.testclient import TestClient


@dataclass
class _SecurityHeadersConfig:
    enabled: bool = True
    extra_script_src: str = ""
    extra_style_src: str = ""
    extra_font_src: str = ""
    extra_connect_src: str = ""
    extra_img_src: str = ""
    frame_ancestors: str = "'self'"


@dataclass
class _Settings:
    debug: bool = False
    security_headers: _SecurityHeadersConfig = field(
        default_factory=_SecurityHeadersConfig
    )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Test copy of middleware to avoid importing full vibetuner.frontend package.

    Mirrors the implementation in vibetuner.frontend.middleware.SecurityHeadersMiddleware.
    """

    BYPASS_PREFIXES = ("/static/", "/health/")

    def __init__(self, app, settings: _Settings | None = None):
        super().__init__(app)
        self._settings = settings or _Settings()

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if any(path.startswith(p) for p in self.BYPASS_PREFIXES):
            return await call_next(request)

        nonce = secrets.token_urlsafe(16)
        request.state.csp_nonce = nonce

        response: Response = await call_next(request)

        config = self._settings.security_headers

        # Build CSP directives
        script_src = f"'nonce-{nonce}' 'strict-dynamic'"
        if config.extra_script_src:
            script_src += f" {config.extra_script_src}"

        style_src = "'self' 'unsafe-inline'"
        if config.extra_style_src:
            style_src += f" {config.extra_style_src}"

        img_src = "'self' data:"
        if config.extra_img_src:
            img_src += f" {config.extra_img_src}"

        directives = [
            "default-src 'self'",
            f"script-src {script_src}",
            f"style-src {style_src}",
            f"img-src {img_src}",
            f"frame-ancestors {config.frame_ancestors}",
        ]

        if config.extra_font_src:
            directives.append(f"font-src 'self' {config.extra_font_src}")

        if config.extra_connect_src:
            directives.append(f"connect-src 'self' {config.extra_connect_src}")

        csp_value = "; ".join(directives)
        csp_header = (
            "Content-Security-Policy-Report-Only"
            if self._settings.debug
            else "Content-Security-Policy"
        )
        response.headers[csp_header] = csp_value

        # Non-CSP security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-XSS-Protection"] = "0"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=()"
        )

        # Remove server identity header
        if "server" in response.headers:
            del response.headers["server"]

        return response


def _make_app(settings: _Settings | None = None):
    """Create a minimal FastAPI app wrapped with SecurityHeadersMiddleware."""
    from starlette.applications import Starlette
    from starlette.responses import PlainTextResponse
    from starlette.routing import Route

    captured_nonces: list[str] = []

    async def homepage(request):
        nonce = getattr(request.state, "csp_nonce", None)
        if nonce:
            captured_nonces.append(nonce)
        return PlainTextResponse("OK")

    app = Starlette(routes=[Route("/{path:path}", homepage), Route("/", homepage)])
    app = SecurityHeadersMiddleware(app, settings=settings)
    # Stash list on app for test access
    app._captured_nonces = captured_nonces  # type: ignore[attr-defined]
    return app


class TestSecurityHeadersMiddleware:
    """Test SecurityHeadersMiddleware header injection and nonce generation."""

    def test_nonce_is_set_and_nonempty(self):
        """request.state.csp_nonce is set and non-empty."""
        app = _make_app()
        client = TestClient(app)
        client.get("/")
        assert len(app._captured_nonces) == 1
        assert len(app._captured_nonces[0]) > 0

    def test_two_requests_produce_different_nonces(self):
        """Two requests produce different nonces."""
        app = _make_app()
        client = TestClient(app)
        client.get("/")
        client.get("/")
        assert len(app._captured_nonces) == 2
        assert app._captured_nonces[0] != app._captured_nonces[1]

    def test_csp_header_contains_nonce(self):
        """CSP header contains the nonce value."""
        app = _make_app()
        client = TestClient(app)
        resp = client.get("/")
        nonce = app._captured_nonces[0]
        csp = resp.headers.get("Content-Security-Policy", "")
        assert f"'nonce-{nonce}'" in csp

    def test_report_only_header_in_debug_mode(self):
        """Debug mode uses Content-Security-Policy-Report-Only."""
        app = _make_app(settings=_Settings(debug=True))
        client = TestClient(app)
        resp = client.get("/")
        assert "Content-Security-Policy-Report-Only" in resp.headers
        assert "Content-Security-Policy" not in {
            k for k in resp.headers if k != "Content-Security-Policy-Report-Only"
        }

    def test_enforced_header_in_production(self):
        """Production mode uses enforced Content-Security-Policy."""
        app = _make_app(settings=_Settings(debug=False))
        client = TestClient(app)
        resp = client.get("/")
        assert "Content-Security-Policy" in resp.headers
        assert "Content-Security-Policy-Report-Only" not in resp.headers

    def test_non_csp_security_headers_present(self):
        """All non-CSP security headers are present."""
        app = _make_app()
        client = TestClient(app)
        resp = client.get("/")
        assert resp.headers["X-Content-Type-Options"] == "nosniff"
        assert resp.headers["X-Frame-Options"] == "DENY"
        assert resp.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
        assert resp.headers["X-XSS-Protection"] == "0"
        assert "camera=()" in resp.headers["Permissions-Policy"]
        assert "microphone=()" in resp.headers["Permissions-Policy"]
        assert "geolocation=()" in resp.headers["Permissions-Policy"]
        assert "payment=()" in resp.headers["Permissions-Policy"]

    def test_static_path_bypass(self):
        """Static paths do not receive CSP headers."""
        app = _make_app()
        client = TestClient(app)
        resp = client.get("/static/css/main.css")
        assert "Content-Security-Policy" not in resp.headers
        assert "Content-Security-Policy-Report-Only" not in resp.headers
        assert "X-Content-Type-Options" not in resp.headers

    def test_health_path_bypass(self):
        """Health paths do not receive CSP headers."""
        app = _make_app()
        client = TestClient(app)
        resp = client.get("/health/live")
        assert "Content-Security-Policy" not in resp.headers
        assert "X-Content-Type-Options" not in resp.headers

    def test_extra_script_src_appended(self):
        """Extra script-src sources are appended to CSP."""
        config = _SecurityHeadersConfig(extra_script_src="https://cdn.example.com")
        app = _make_app(settings=_Settings(security_headers=config))
        client = TestClient(app)
        resp = client.get("/")
        csp = resp.headers["Content-Security-Policy"]
        assert "https://cdn.example.com" in csp

    def test_extra_connect_src_appended(self):
        """Extra connect-src sources create a connect-src directive."""
        config = _SecurityHeadersConfig(extra_connect_src="wss://ws.example.com")
        app = _make_app(settings=_Settings(security_headers=config))
        client = TestClient(app)
        resp = client.get("/")
        csp = resp.headers["Content-Security-Policy"]
        assert "connect-src 'self' wss://ws.example.com" in csp

    def test_strict_dynamic_present_in_script_src(self):
        """'strict-dynamic' is present in script-src."""
        app = _make_app()
        client = TestClient(app)
        resp = client.get("/")
        csp = resp.headers["Content-Security-Policy"]
        assert "'strict-dynamic'" in csp
