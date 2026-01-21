import warnings
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, Request


async def require_htmx(request: Request) -> None:
    if not request.state.htmx:
        raise HTTPException(status_code=400, detail="HTMX header not found")


async def enforce_lang(request: Request, lang: Optional[str] = None):
    if lang is None or lang != request.state.language:
        redirect_url = request.url_for(
            request.scope["endpoint"].__name__,
            **{**request.path_params, "lang": request.state.language},
        ).path
        raise HTTPException(
            status_code=307,
            detail=f"Redirecting to canonical language: {request.state.language}",
            headers={"Location": redirect_url},
        )

    return request.state.language


LangDep = Annotated[str, Depends(enforce_lang)]


async def require_lang_prefix(request: Request) -> None:
    """Dependency for localized routes.

    .. deprecated::
        Use `LocalizedRouter(localized=True)` or the `@localized` decorator instead.
        This dependency will be removed in a future version.

    - Anonymous: serve at unprefixed URL (default/detected language)
    - Authenticated: 301 redirect to /{lang}/{path}
    """
    warnings.warn(
        "LangPrefixDep is deprecated. Use LocalizedRouter(localized=True) "
        "or the @localized decorator instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    # If accessed with prefix, we're good
    if hasattr(request.state, "lang_prefix"):
        return

    # Check if endpoint is marked as localized
    endpoint = request.scope.get("endpoint")
    if endpoint and not getattr(endpoint, "_localized", True):
        return  # Non-localized route

    # Anonymous users: no redirect (serve default/detected language)
    if not request.user.is_authenticated:
        return

    # Authenticated user without prefix: 301 redirect to prefixed URL
    lang = request.state.language
    prefixed_url = f"/{lang}{request.url.path}"
    if request.url.query:
        prefixed_url += f"?{request.url.query}"

    raise HTTPException(status_code=301, headers={"Location": prefixed_url})


LangPrefixDep = Annotated[None, Depends(require_lang_prefix)]


MAGIC_COOKIE_NAME = "magic_access"


def require_magic_cookie(request: Request) -> None:
    """Dependency to check if the magic access cookie is present."""
    if MAGIC_COOKIE_NAME not in request.cookies:
        raise HTTPException(status_code=403, detail="Access forbidden")

    if request.cookies[MAGIC_COOKIE_NAME] != "granted":
        raise HTTPException(status_code=403, detail="Access forbidden")


MagicCookieDep = Depends(require_magic_cookie)
