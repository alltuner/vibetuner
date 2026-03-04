# ABOUTME: Route decorators for vibetuner.
# ABOUTME: Provides @cache_control for declarative HTTP cache headers.
import functools
import inspect
from collections.abc import Callable
from typing import Any


# Maps keyword argument names to their Cache-Control directive strings.
# Boolean directives map to a bare directive name; int directives include a value.
_BOOL_DIRECTIVES = {
    "public": "public",
    "private": "private",
    "no_cache": "no-cache",
    "no_store": "no-store",
    "must_revalidate": "must-revalidate",
    "immutable": "immutable",
}

_VALUE_DIRECTIVES = {
    "max_age": "max-age",
    "s_maxage": "s-maxage",
    "stale_while_revalidate": "stale-while-revalidate",
}


def _build_cache_control_header(**kwargs: Any) -> str:
    """Build a Cache-Control header value from keyword arguments."""
    directives: list[str] = []
    for kwarg, directive in _BOOL_DIRECTIVES.items():
        if kwargs.get(kwarg):
            directives.append(directive)
    for kwarg, directive in _VALUE_DIRECTIVES.items():
        value = kwargs.get(kwarg)
        if value is not None:
            directives.append(f"{directive}={value}")
    return ", ".join(directives)


def cache_control(
    *,
    max_age: int | None = None,
    s_maxage: int | None = None,
    public: bool = False,
    private: bool = False,
    no_cache: bool = False,
    no_store: bool = False,
    must_revalidate: bool = False,
    stale_while_revalidate: int | None = None,
    immutable: bool = False,
) -> Callable:
    """Decorator that sets ``Cache-Control`` HTTP headers on route responses.

    Eliminates manual ``response.headers["Cache-Control"] = ...`` boilerplate.

    Args:
        max_age: Max age in seconds for the response to be considered fresh.
        s_maxage: Max age for shared caches (CDNs, proxies).
        public: Response can be stored by any cache.
        private: Response is specific to the user (no shared cache).
        no_cache: Cache must revalidate before each use.
        no_store: Do not cache the response at all.
        must_revalidate: Stale response must not be used without revalidation.
        stale_while_revalidate: Seconds a stale response can be served while
            revalidating in the background.
        immutable: Response body will never change (for versioned assets).

    Example::

        @router.get("/static-page")
        @cache_control(max_age=300, public=True)
        async def static_page(request: Request):
            return render_template("static_page.html.jinja", request)

        @router.get("/api/data")
        @cache_control(no_store=True)
        async def api_data():
            return {"data": "sensitive"}
    """
    header_value = _build_cache_control_header(
        max_age=max_age,
        s_maxage=s_maxage,
        public=public,
        private=private,
        no_cache=no_cache,
        no_store=no_store,
        must_revalidate=must_revalidate,
        stale_while_revalidate=stale_while_revalidate,
        immutable=immutable,
    )

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if inspect.iscoroutinefunction(func):
                response = await func(*args, **kwargs)
            else:
                response = func(*args, **kwargs)

            if hasattr(response, "headers"):
                response.headers["Cache-Control"] = header_value

            return response

        return wrapper

    return decorator
