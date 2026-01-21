from fastapi import Request, Response
from fastapi.middleware import Middleware
from fastapi.requests import HTTPConnection
from starlette.authentication import AuthCredentials, AuthenticationBackend
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
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
from starlette_htmx.middleware import HtmxMiddleware

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


class AdjustLangCookieMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        lang_cookie = request.cookies.get("language")
        if not lang_cookie or lang_cookie != request.state.language:
            response.set_cookie(
                key="language",
                value=request.state.language,
                max_age=LANGUAGE_COOKIE_MAX_AGE,
            )

        return response


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


middlewares: list[Middleware] = [
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
        selectors=[
            LocaleFromQuery(query_param="l"),
            locale_selector,
            user_preference_selector,
            LocaleFromCookie(),
            LocaleFromHeader(),
        ],
    ),
    Middleware(LangPrefixMiddleware, supported_languages=ctx.supported_languages),
    Middleware(AdjustLangCookieMiddleware),
    Middleware(AuthenticationMiddleware, backend=AuthBackend()),
]
