# ABOUTME: Router with explicit localization control for SEO-friendly URLs
# ABOUTME: Allows marking routes as localized/non-localized at the router level

from fastapi import APIRouter


class LocalizedRouter(APIRouter):
    """Router with explicit localization control.

    Use this router to control whether routes should use language-prefixed URLs
    for SEO purposes.

    Args:
        localized: If True, mark all routes as requiring language prefix.
                   If False, mark as non-localized (no prefix).
                   If None (default), no marking is applied.
        *args, **kwargs: Standard APIRouter arguments (prefix, tags, etc.)

    Example:
        # Force localization for all routes in this router
        router = LocalizedRouter(prefix="/legal", localized=True)

        @router.get("/privacy")
        async def privacy():
            pass  # Will require /{lang}/legal/privacy

        # Force non-localization
        api_router = LocalizedRouter(prefix="/api", localized=False)

        @api_router.get("/users")
        async def users():
            pass  # Will only be available at /api/users
    """

    def __init__(self, *args, localized: bool | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._localized = localized

    def add_api_route(self, path, endpoint, **kwargs):
        if not hasattr(endpoint, "_localized"):
            if self._localized is not None:
                endpoint._localized = self._localized
        return super().add_api_route(path, endpoint, **kwargs)
