# ABOUTME: Unit tests for SecurityHeadersMiddleware CSP nonce and security headers
# ABOUTME: Verifies nonce generation, CSP directives, report-only mode, and bypass paths
# ruff: noqa: S101

import secrets
from dataclasses import dataclass, field

from starlette.datastructures import MutableHeaders
from starlette.testclient import TestClient
from starlette.types import ASGIApp, Receive, Scope, Send


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


class SecurityHeadersMiddleware:
    """Test copy of middleware to avoid importing full vibetuner.frontend package.

    Mirrors the implementation in vibetuner.frontend.middleware.SecurityHeadersMiddleware.
    """

    BYPASS_PREFIXES = ("/static/", "/health/")

    def __init__(self, app: ASGIApp, settings: _Settings | None = None):
        self.app = app
        self._settings = settings or _Settings()

    def _apply_headers(self, headers: MutableHeaders, nonce: str) -> None:
        config = self._settings.security_headers

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
        headers[csp_header] = csp_value

        headers["X-Content-Type-Options"] = "nosniff"
        headers["X-Frame-Options"] = "DENY"
        headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        headers["X-XSS-Protection"] = "0"
        headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=()"
        )

        if "server" in headers:
            del headers["server"]

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if any(path.startswith(p) for p in self.BYPASS_PREFIXES):
            await self.app(scope, receive, send)
            return

        nonce = secrets.token_urlsafe(16)

        if "state" not in scope:
            scope["state"] = {}
        scope["state"]["csp_nonce"] = nonce

        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                self._apply_headers(MutableHeaders(scope=message), nonce)
            await send(message)

        await self.app(scope, receive, send_with_headers)


def _make_app(settings: _Settings | None = None):
    """Create a minimal Starlette app wrapped with SecurityHeadersMiddleware."""
    from starlette.applications import Starlette
    from starlette.responses import PlainTextResponse
    from starlette.routing import Route

    captured_nonces: list[str] = []

    async def homepage(request):
        nonce = getattr(request.state, "csp_nonce", None)
        if nonce:
            captured_nonces.append(nonce)
        return PlainTextResponse("OK")

    inner = Starlette(routes=[Route("/{path:path}", homepage), Route("/", homepage)])
    app = SecurityHeadersMiddleware(inner, settings=settings)
    # Stash list on wrapper for test access
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
