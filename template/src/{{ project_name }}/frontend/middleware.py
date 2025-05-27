from fastapi.middleware import Middleware
from fastapi.requests import HTTPConnection
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette_babel import (
    LocaleFromQuery,
    LocaleMiddleware,
    get_translator,
)
from starlette_cramjam.middleware import CompressionMiddleware  # type: ignore

from .. import paths
from .lifespan import ctx


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
shared_translator.load_from_directories([paths.locales])


# Override below this line

# Until this line

middlewares: list[Middleware] = [
    Middleware(CompressionMiddleware),
    Middleware(TrustedHostMiddleware),
    Middleware(
        LocaleMiddleware,
        locales=ctx.supported_languages,
        default_locale=ctx.default_language,
        selectors=[LocaleFromQuery(query_param="l"), locale_selector],
    ),
    Middleware(SessionMiddleware, secret_key=ctx.session_key),
    # Add your middleware below this line
]

# EOF
