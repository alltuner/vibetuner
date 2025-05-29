from fastapi.middleware import Middleware
from fastapi.requests import HTTPConnection
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette_babel import (
    LocaleFromCookie,
    LocaleFromQuery,
    LocaleMiddleware,
    get_translator,
)
from starlette_compress import CompressMiddleware
from starlette_htmx.middleware import HtmxMiddleware  # type: ignore[import-untyped]

from .. import paths, settings
from .._context import ctx


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

# Override below this line

# Until this line

middlewares: list[Middleware] = [
    Middleware(CompressMiddleware),
    Middleware(TrustedHostMiddleware),
    Middleware(HtmxMiddleware),
    Middleware(
        LocaleMiddleware,
        locales=ctx.supported_languages,
        default_locale=ctx.default_language,
        selectors=[
            LocaleFromQuery(query_param="l"),
            LocaleFromCookie(),
            locale_selector,
        ],
    ),
    Middleware(SessionMiddleware, secret_key=settings.session_key),
    # Add your middleware below this line
]

# EOF
