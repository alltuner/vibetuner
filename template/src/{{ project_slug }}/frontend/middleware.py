from fastapi import Request, Response
from fastapi.middleware import Middleware
from fastapi.requests import HTTPConnection
from starlette.authentication import AuthCredentials, AuthenticationBackend
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette_babel import (
    LocaleFromCookie,
    LocaleFromQuery,
    LocaleMiddleware,
    get_translator,
)
from starlette_compress import CompressMiddleware
from starlette_htmx.middleware import HtmxMiddleware  # type: ignore[import-untyped]

from ..core import paths
from ..core.config import settings
from .context import ctx
from .oauth import WebUser


def locale_selector(conn: HTTPConnection) -> str | None:
    """
    Selects the locale based on the first part of the path if it matches a 2-letter language code.
    """

    parts = conn.scope.get("path", "").strip("/").split("/")

    # Check if first part is a 2-letter lowercase language code
    if parts and len(parts[0]) == 2 and parts[0].islower() and parts[0].isalpha():
        return parts[0]

    return None


shared_translator = get_translator()
if paths.locales.exists() and paths.locales.is_dir():
    # Load translations from the locales directory
    shared_translator.load_from_directories([paths.locales])


class AdjustLangCookieMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        lang_cookie = request.cookies.get("language")
        if not lang_cookie or lang_cookie != request.state.language:
            response.set_cookie(
                key="language", value=request.state.language, max_age=3600
            )

        return response


class ForwardedProtocolMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    # Based on https://github.com/encode/uvicorn/blob/master/uvicorn/middleware/proxy_headers.py
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "lifespan":
            return await self.app(scope, receive, send)

        headers = dict(scope["headers"])

        if b"x-forwarded-proto" in headers:
            x_forwarded_proto = headers[b"x-forwarded-proto"].decode("latin1").strip()

            if x_forwarded_proto in {"http", "https", "ws", "wss"}:
                if scope["type"] == "websocket":
                    scope["scheme"] = x_forwarded_proto.replace("http", "ws")
                else:
                    scope["scheme"] = x_forwarded_proto

        return await self.app(scope, receive, send)


class AuthBackend(AuthenticationBackend):
    async def authenticate(
        self,
        conn: HTTPConnection,
    ) -> tuple[AuthCredentials, WebUser] | None:
        if user := conn.session.get("user"):
            try:
                return (AuthCredentials(["authenticated"]), WebUser.model_validate(user))
            except Exception:
                # Clear corrupted session data and continue unauthenticated
                conn.session.pop("user", None)
                return None

        return None


# Until this line
middlewares: list[Middleware] = [
    Middleware(CompressMiddleware),
    Middleware(TrustedHostMiddleware),
    Middleware(ForwardedProtocolMiddleware),
    Middleware(HtmxMiddleware),
    Middleware(
        LocaleMiddleware,
        locales=list(ctx.supported_languages),
        default_locale=ctx.default_language,
        selectors=[
            LocaleFromQuery(query_param="l"),
            locale_selector,
            LocaleFromCookie(),
        ],
    ),
    Middleware(AdjustLangCookieMiddleware),
    Middleware(SessionMiddleware, secret_key=settings.session_key.get_secret_value()),
    Middleware(AuthenticationMiddleware, backend=AuthBackend()),
    # Add your middleware below this line
]

# EOF
