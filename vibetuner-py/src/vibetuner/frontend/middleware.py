import logging
import re
import secrets

from fastapi.middleware import Middleware
from fastapi.requests import HTTPConnection
from starlette.authentication import AuthCredentials, AuthenticationBackend
from starlette.datastructures import MutableHeaders
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.responses import Response as StarletteResponse
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette_babel import (
    LocaleFromCookie,
    LocaleFromHeader,
    LocaleFromQuery,
    LocaleMiddleware,
    get_translator,
)
from starlette_context.middleware import RawContextMiddleware
from starlette_context.plugins import RequestIdPlugin
from starlette_htmx.middleware import HtmxDetails

from vibetuner.config import settings
from vibetuner.context import ctx
from vibetuner.paths import locales as locales_path

from .oauth import WebUser


# Cookie expiry: 1 year in seconds
LANGUAGE_COOKIE_MAX_AGE = 365 * 24 * 60 * 60  # 31536000


def locale_selector(conn: HTTPConnection) -> str | None:
    """
    Selects the locale based on the first part of the path if it matches a 2-letter language code.
    """

    parts = conn.scope.get("path", "").strip("/").split("/")

    # Check if first part is a 2-letter lowercase language code
    if parts and len(parts[0]) == 2 and parts[0].islower() and parts[0].isalpha():
        return parts[0]

    return None


def user_preference_selector(conn: HTTPConnection) -> str | None:
    """
    Selects the locale based on authenticated user's language preference from session.
    This takes priority over all other locale selectors to avoid database queries.
    """
    # Check if session is available in scope
    if "session" not in conn.scope:
        return None

    session = conn.scope["session"]
    if not session:
        return None

    user_data = session.get("user")
    if not user_data:
        return None

    # Get language preference from user settings stored in session
    user_settings = user_data.get("settings")
    if not user_settings:
        return None

    language = user_settings.get("language")
    if language and isinstance(language, str) and len(language) == 2:
        return language.lower()

    return None


shared_translator = get_translator()
if locales_path is not None and locales_path.exists() and locales_path.is_dir():
    # Load translations from the locales directory
    shared_translator.load_from_directories([locales_path])


class HtmxMiddleware:
    """Pure ASGI replacement for starlette_htmx.middleware.HtmxMiddleware.

    The upstream starlette-htmx uses BaseHTTPMiddleware, which adds an extra
    empty sentinel body chunk on response completion. This triggers a bug in
    slowapi's SlowAPIASGIMiddleware where http.response.start is re-sent on
    every body chunk, causing "ASGI flow error: Response already started".
    See: https://github.com/laurentS/slowapi/issues/XXX

    This pure ASGI version avoids the issue. Can be removed once slowapi
    fixes SlowAPIASGIMiddleware upstream.
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            from starlette.requests import Request

            request = Request(scope)
            scope.setdefault("state", {})["htmx"] = HtmxDetails(request)
        await self.app(scope, receive, send)


_logger = logging.getLogger("vibetuner.security")

_SCRIPT_WITHOUT_NONCE_RE = re.compile(rb"<script(?![^>]*\snonce=)", re.IGNORECASE)
_EMPTY_NONCE_RE = re.compile(rb'<script[^>]*\snonce=""\s*', re.IGNORECASE)


class SecurityHeadersMiddleware:
    """Pure ASGI middleware that adds security headers (CSP with nonce, etc.) to responses.

    Converted from BaseHTTPMiddleware to avoid triggering a bug in slowapi's
    SlowAPIASGIMiddleware that re-sends http.response.start on every body chunk.
    Can revert to BaseHTTPMiddleware once slowapi fixes the issue upstream.
    """

    BYPASS_PREFIXES = ("/static/", "/health/")

    def __init__(self, app: ASGIApp):
        self.app = app

    def _apply_headers(self, headers: MutableHeaders, nonce: str) -> None:
        config = settings.security_headers

        script_src = f"'nonce-{nonce}' 'strict-dynamic'"
        if config.extra_script_src:
            script_src += f" {config.extra_script_src}"

        style_src = "'self' 'unsafe-inline'"
        if config.extra_style_src:
            style_src += f" {config.extra_style_src}"

        img_src = "'self' data:"
        if config.extra_img_src:
            img_src += f" {config.extra_img_src}"

        media_src = "'self' blob:"
        if config.extra_media_src:
            media_src += f" {config.extra_media_src}"

        directives = [
            "default-src 'self'",
            f"script-src {script_src}",
            f"style-src {style_src}",
            f"img-src {img_src}",
            f"media-src {media_src}",
            f"frame-ancestors {config.frame_ancestors}",
        ]

        if config.extra_font_src:
            directives.append(f"font-src 'self' {config.extra_font_src}")

        if config.extra_connect_src:
            directives.append(f"connect-src 'self' {config.extra_connect_src}")

        csp_value = "; ".join(directives)
        csp_header = (
            "Content-Security-Policy-Report-Only"
            if settings.debug
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

    @staticmethod
    def _inject_nonces(body: bytes, nonce: str) -> bytes:
        if _EMPTY_NONCE_RE.search(body):
            _logger.warning(
                "Found <script> tag with empty nonce attribute. "
                "CSP nonces are auto-injected by SecurityHeadersMiddleware; "
                "do not add nonce= attributes manually in templates."
            )
        replacement = f'<script nonce="{nonce}"'.encode()
        return _SCRIPT_WITHOUT_NONCE_RE.sub(replacement, body)

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

        initial_message = None
        is_html = False
        body_parts: list[bytes] = []

        async def send_with_headers(message):
            nonlocal initial_message, is_html

            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                self._apply_headers(headers, nonce)
                content_type = headers.get("content-type", "")
                is_html = "text/html" in content_type
                if is_html:
                    initial_message = message
                else:
                    await send(message)
                return

            if message["type"] == "http.response.body":
                if not is_html:
                    await send(message)
                    return

                body_parts.append(message.get("body", b""))
                more_body = message.get("more_body", False)
                if not more_body:
                    full_body = self._inject_nonces(b"".join(body_parts), nonce)
                    headers = MutableHeaders(scope=initial_message)
                    headers["content-length"] = str(len(full_body))
                    await send(initial_message)
                    await send({"type": "http.response.body", "body": full_body})
                return

            await send(message)

        await self.app(scope, receive, send_with_headers)


class AdjustLangCookieMiddleware:
    """Pure ASGI middleware that syncs the language cookie with request.state.language.

    Converted from BaseHTTPMiddleware to avoid triggering a bug in slowapi's
    SlowAPIASGIMiddleware that re-sends http.response.start on every body chunk.
    Can revert to BaseHTTPMiddleware once slowapi fixes the issue upstream.
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

        # Parse language cookie from request headers
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


class LangPrefixMiddleware:
    """Strips valid language prefixes from URL paths before routing.

    Supports SEO-friendly path-prefix language routing (e.g., /ca/dashboard -> /dashboard
    with lang=ca). Invalid language prefixes return 404; bypass paths like /static/,
    /health/, /debug/ pass through unchanged.
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


class AuthBackend(AuthenticationBackend):
    async def authenticate(
        self,
        conn: HTTPConnection,
    ) -> tuple[AuthCredentials, WebUser] | None:
        if user := conn.session.get("user"):
            try:
                return (
                    AuthCredentials(["authenticated"]),
                    WebUser.model_validate(user),
                )
            except Exception:
                # Clear corrupted session data and continue unauthenticated
                conn.session.pop("user", None)
                return None

        return None


def _build_locale_selectors() -> list:
    """Build locale selector list based on configuration.

    Selectors are evaluated in order. The first one that returns
    a valid locale wins. Order is fixed by design:
    1. query_param - ?l=ca query parameter
    2. url_prefix - /ca/... path prefix
    3. user_session - authenticated user's stored preference
    4. cookie - language cookie
    5. accept_language - browser Accept-Language header
    """
    selectors: list = []
    config = settings.locale_detection

    if config.query_param:
        selectors.append(LocaleFromQuery(query_param="l"))
    if config.url_prefix:
        selectors.append(locale_selector)
    if config.user_session:
        selectors.append(user_preference_selector)
    if config.cookie:
        selectors.append(LocaleFromCookie())
    if config.accept_language:
        selectors.append(LocaleFromHeader(supported_locales=ctx.supported_languages))

    return selectors


middlewares: list[Middleware] = [
    Middleware(RawContextMiddleware, plugins=[RequestIdPlugin(validate=False)]),
]

if settings.rate_limit.enabled:
    # SlowAPIASGIMiddleware has a bug where it re-sends http.response.start on
    # every body chunk, crashing streaming responses (FileResponse).
    # Using SlowAPIMiddleware (BaseHTTPMiddleware-based) as workaround.
    # See: https://github.com/laurentS/slowapi/issues/XXX
    from slowapi.middleware import SlowAPIMiddleware

    middlewares.append(Middleware(SlowAPIMiddleware))

if settings.security_headers.enabled:
    middlewares.append(Middleware(SecurityHeadersMiddleware))

middlewares += [
    Middleware(TrustedHostMiddleware),
    Middleware(HtmxMiddleware),
    Middleware(
        SessionMiddleware,
        secret_key=settings.session_key.get_secret_value(),
        https_only=not ctx.DEBUG,
    ),
    Middleware(
        LocaleMiddleware,
        locales=list(ctx.supported_languages),
        default_locale=ctx.default_language,
        selectors=_build_locale_selectors(),
    ),
    Middleware(LangPrefixMiddleware, supported_languages=ctx.supported_languages),
    Middleware(AdjustLangCookieMiddleware),
    Middleware(AuthenticationMiddleware, backend=AuthBackend()),
]
