import asyncio
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
from vibetuner.logging import logger
from vibetuner.paths import locales as locales_path, package_locales

from .oauth import WebUser


# Cookie expiry: 1 year in seconds
LANGUAGE_COOKIE_MAX_AGE = 365 * 24 * 60 * 60  # 31536000


def locale_selector(conn: HTTPConnection) -> str | None:
    """Selects the locale from the language prefix extracted by LangPrefixMiddleware."""
    return conn.scope.get("state", {}).get("lang_prefix")


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

# Load the framework's bundled catalogs first so every consuming app gets
# translated framework templates (login, profile, email_sent, etc.) without
# having to re-extract those strings into its own catalog. The project's
# locales/ directory loads second; starlette_babel's Translator merges
# domains in load order, so app translations override framework strings on
# collision.
if package_locales is not None:
    shared_translator.load_from_directories([package_locales])

if locales_path is not None and locales_path.exists() and locales_path.is_dir():
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

        if config.style_src_strict:
            style_src = f"'self' 'nonce-{nonce}'"
        else:
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
        report_only = settings.debug and not config.enforce_csp_in_debug
        csp_header = (
            "Content-Security-Policy-Report-Only"
            if report_only
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

        # Pair nosniff with a fallback Content-Type. A bare Response() with no
        # media_type sends nosniff + missing Content-Type, which Safari/Firefox
        # turn into a 0-byte download and Chrome turns into a generic error.
        if "content-type" not in headers:
            headers["Content-Type"] = "text/plain; charset=utf-8"

        if "server" in headers:
            del headers["server"]

    @staticmethod
    def _inject_nonces(body: bytes, nonce: str) -> bytes:
        if _EMPTY_NONCE_RE.search(body):
            logger.warning(
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


# Upper bound for /debug/tasks/queue and /debug/tasks/workers requests.
# Streaq's UI walks Redis with SCAN; on shared or large Redis instances the
# walk can take much longer than a debug page is worth waiting for. The
# request is cancelled and a 504 is returned instead of hanging the browser.
# See upstream tastyware/streaq#163.
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
    """Bounds Streaq debug UI requests that walk Redis with SCAN.

    Streaq's /queue and /workers endpoints SCAN Redis to enumerate tasks and
    worker health keys. On a shared or large Redis they can hang indefinitely,
    leaving the browser with no response. This middleware cancels any such
    request that exceeds STREAQ_DEBUG_REQUEST_TIMEOUT_SECONDS and replies with
    a 504 page explaining what happened. Cheap endpoints under /debug/tasks
    (e.g. /cron) are not guarded and pass through unchanged.
    """

    def __init__(self, app: ASGIApp):
        self.app = app

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
                self.app(scope, receive, send_tracking),
                timeout=STREAQ_DEBUG_REQUEST_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            logger.warning(
                "Streaq debug request timed out after "
                f"{STREAQ_DEBUG_REQUEST_TIMEOUT_SECONDS}s: {path}"
            )
            if response_started:
                # Cannot send a fresh response once headers are out; the
                # client will see a truncated body. Logging is enough.
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
                {
                    "type": "http.response.body",
                    "body": _STREAQ_DEBUG_TIMEOUT_BODY,
                }
            )


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
            except Exception as exc:
                logger.warning(
                    "Clearing invalid session user data: {exc}",
                    exc=exc,
                    session_user_keys=sorted(user.keys())
                    if isinstance(user, dict)
                    else None,
                )
                conn.session.pop("user", None)
                return None

        return None


def _build_locale_selectors() -> list:
    """Build locale selector list based on configuration.

    Selectors are evaluated in order. The first one that returns
    a valid locale wins. Order is fixed by design:
    0. user-registered resolvers (vibetuner.i18n.register_locale_resolver)
    1. query_param - ?l=ca query parameter
    2. url_prefix - /ca/... path prefix
    3. user_session - authenticated user's stored preference
    4. cookie - language cookie
    5. accept_language - browser Accept-Language header
    """
    from vibetuner.i18n import combined_locale_selector

    selectors: list = [combined_locale_selector]
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
    # LangPrefixMiddleware must run before LocaleMiddleware so that
    # state["lang_prefix"] is populated when locale_selector evaluates it.
    # Middleware listed earlier wraps middleware listed later, so the earlier
    # one runs first on the request path.
    Middleware(LangPrefixMiddleware, supported_languages=ctx.supported_languages),
    Middleware(
        LocaleMiddleware,
        locales=list(ctx.supported_languages),
        default_locale=ctx.default_language,
        selectors=_build_locale_selectors(),
    ),
    Middleware(AdjustLangCookieMiddleware),
    Middleware(AuthenticationMiddleware, backend=AuthBackend()),
]

if settings.workers_available:
    # Innermost so the timeout only cancels the Streaq handler itself rather
    # than work performed by outer middlewares.
    middlewares.append(Middleware(StreaqDebugTimeoutMiddleware))
