# ABOUTME: Router with explicit localization control for SEO-friendly URLs
# ABOUTME: Allows marking routes as localized/non-localized at the router level

from collections.abc import Callable
from functools import wraps
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request


async def _localized_redirect(request: Request) -> None:
    """Dependency that handles language prefix redirects for localized routes.

    - If accessed with language prefix: pass through
    - Anonymous users: no redirect (serve at unprefixed URL)
    - Authenticated users: 301 redirect to /{lang}/path
    """
    # If accessed with prefix, we're good
    if hasattr(request.state, "lang_prefix"):
        return

    # Anonymous users: no redirect (serve default/detected language)
    if not request.user.is_authenticated:
        return

    # Authenticated user without prefix: 301 redirect to prefixed URL
    lang = request.state.language
    prefixed_url = f"/{lang}{request.url.path}"
    if request.url.query:
        prefixed_url += f"?{request.url.query}"

    raise HTTPException(status_code=301, headers={"Location": prefixed_url})


class LocalizedRouter(APIRouter):
    """Router with automatic localization handling.

    When localized=True, routes automatically redirect authenticated users to
    language-prefixed URLs while serving anonymous users at unprefixed URLs
    (optimal for SEO).

    Args:
        localized: If True, enable language prefix redirects for authenticated users.
                   If False, routes are non-localized (no redirects).
                   If None (default), no automatic handling.
        *args, **kwargs: Standard APIRouter arguments (prefix, tags, etc.)

    Example:
        # All routes in this router handle language prefixes automatically
        router = LocalizedRouter(prefix="/legal", localized=True)

        @router.get("/privacy")
        async def privacy(request: Request):
            return render_template("privacy.html.jinja", request)
            # Anonymous: served at /legal/privacy
            # Authenticated: redirected to /{lang}/legal/privacy

        # Non-localized routes (API endpoints)
        api_router = LocalizedRouter(prefix="/api", localized=False)

        @api_router.get("/users")
        async def users():
            return {"users": []}  # Always at /api/users, no redirects
    """

    def __init__(self, *args, localized: bool | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._localized = localized

    def add_api_route(self, path, endpoint, **kwargs):
        # Mark endpoint with localization setting
        if not hasattr(endpoint, "_localized"):
            if self._localized is not None:
                endpoint._localized = self._localized

        # Auto-add redirect dependency for localized routes
        if getattr(endpoint, "_localized", False):
            dependencies = list(kwargs.get("dependencies") or [])
            dependencies.append(Depends(_localized_redirect))
            kwargs["dependencies"] = dependencies

        return super().add_api_route(path, endpoint, **kwargs)


def localized(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to mark a route as localized.

    Use this on individual routes when using a regular APIRouter.
    The route will automatically handle language prefix redirects.

    Example:
        router = APIRouter()

        @router.get("/privacy")
        @localized
        async def privacy(request: Request):
            return render_template("privacy.html.jinja", request)
    """
    func._localized = True

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Find the request in args or kwargs
        request = kwargs.get("request")
        if request is None:
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

        # Apply redirect logic if we have a request
        if request is not None:
            await _localized_redirect(request)

        return await func(*args, **kwargs)

    # Preserve the _localized attribute on wrapper
    wrapper._localized = True
    return wrapper
