# ABOUTME: Jinja2 template rendering for HTML responses.
# ABOUTME: Lives outside vibetuner.frontend to avoid circular imports with tune.py.
import functools
import inspect
import threading
from collections.abc import Callable
from datetime import date, datetime, timedelta, timezone
from typing import Any

from starlette.requests import Request
from starlette.responses import HTMLResponse, Response, StreamingResponse
from starlette.templating import Jinja2Templates

from vibetuner.context import ctx as data_ctx
from vibetuner.loader import load_app_config
from vibetuner.logging import logger
from vibetuner.paths import frontend_templates
from vibetuner.templates import render_static_template
from vibetuner.time import age_in_timedelta


__all__ = [
    "render",
    "render_static_template",
    "render_template",
    "render_template_block",
    "render_template_blocks",
    "render_template_stream",
    "render_template_string",
    "register_globals",
    "register_context_provider",
    "lang_url_for",
    "url_for_language",
    "hreflang_tags",
]


# App-level template context: static globals and dynamic providers
_context_lock = threading.RLock()
_template_globals: dict[str, Any] = {}
_context_providers: list[Callable[[], dict[str, Any]]] = []
_provider_accepts_request: dict[Callable, bool] = {}


def register_globals(globals_dict: dict[str, Any]) -> None:
    """Register static global variables available in every template.

    Registered globals are merged into the template context on every
    ``render_template()`` call.  User-provided context in the render call
    takes precedence over registered globals.

    Can be called multiple times; later calls merge into existing globals.

    Example::

        from vibetuner.rendering import register_globals

        register_globals({
            "site_title": "My App",
            "og_image": "/static/og.png",
        })
    """
    with _context_lock:
        _template_globals.update(globals_dict)


def register_context_provider(func=None):
    """Register a function that provides template context.

    The decorated function should return a ``dict[str, Any]``.  It will be
    called on every ``render_template()`` invocation and its result merged
    into the context.

    Can be used as a bare decorator or a decorator factory::

        @register_context_provider
        def site_context() -> dict[str, Any]:
            return {"site_title": settings.site_title}

        @register_context_provider()
        def other_context() -> dict[str, Any]:
            return {"analytics_id": "UA-XXX"}
    """
    if func is not None:
        # Used as @register_context_provider (without parentheses)
        with _context_lock:
            _context_providers.append(func)
            _provider_accepts_request[func] = (
                "request" in inspect.signature(func).parameters
            )
        return func

    # Used as @register_context_provider()
    def decorator(fn):
        with _context_lock:
            _context_providers.append(fn)
            _provider_accepts_request[fn] = (
                "request" in inspect.signature(fn).parameters
            )
        return fn

    return decorator


def render(template: str) -> Callable:
    """Decorator that renders a template with the route's return value as context.

    Eliminates ``render_template()`` boilerplate for simple routes. The
    decorated function should return a ``dict`` that becomes the template
    context.  The ``request`` parameter is automatically extracted from the
    route's arguments.

    If the route returns a :class:`~starlette.responses.Response` (e.g.
    ``HTMLResponse`` or ``RedirectResponse``), it is passed through unchanged
    — this is the escape hatch for conditional logic.

    Example::

        @router.get("/")
        @render("items/list.html.jinja")
        async def index(request: Request) -> dict:
            items = await Item.find_all().to_list()
            return {"items": items}

    Args:
        template: Path to template file relative to ``templates/frontend/``.

    Returns:
        Decorator that wraps the route function.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Response:
            # Extract request from kwargs or positional args
            request = kwargs.get("request")
            if request is None:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            if request is None:
                raise TypeError(
                    f"@render('{template}'): route '{func.__name__}' must accept "
                    "a 'request' parameter"
                )

            if inspect.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Escape hatch: pass through Response objects unchanged
            if isinstance(result, Response):
                return result

            if not isinstance(result, dict):
                raise TypeError(
                    f"@render('{template}'): route '{func.__name__}' must return "
                    f"a dict or Response, got {type(result).__name__}"
                )

            return render_template(template, request, result)

        return wrapper

    return decorator


def _collect_provider_context(request: Request | None = None) -> dict[str, Any]:
    """Run all registered context providers and merge results.

    Providers that accept a ``request`` parameter will receive the current
    request object.  Providers with no parameters continue to work unchanged.
    """
    with _context_lock:
        providers = list(_context_providers)
    result: dict[str, Any] = {}
    for provider in providers:
        try:
            accepts_request = _provider_accepts_request.get(provider, False)
            if accepts_request and request is not None:
                ctx = provider(request=request)
            else:
                ctx = provider()
            if isinstance(ctx, dict):
                result.update(ctx)
            else:
                logger.error(
                    f"Context provider '{provider.__name__}' returned "
                    f"{type(ctx).__name__} instead of dict, skipping"
                )
        except Exception as e:
            logger.error(f"Context provider '{provider.__name__}' failed: {e}")
    return result


def _timeago_verbose(diff: timedelta, dt) -> str:
    """Format timedelta as verbose relative time string."""
    from starlette_babel import gettext_lazy as _

    ngettext = _
    if diff < timedelta(seconds=60):
        seconds = diff.seconds
        return ngettext(
            "%(seconds)d second ago",
            "%(seconds)d seconds ago",
            seconds,
        ) % {"seconds": seconds}
    if diff < timedelta(minutes=60):
        minutes = diff.seconds // 60
        return ngettext(
            "%(minutes)d minute ago",
            "%(minutes)d minutes ago",
            minutes,
        ) % {"minutes": minutes}
    if diff < timedelta(days=1):
        hours = diff.seconds // 3600
        return ngettext("%(hours)d hour ago", "%(hours)d hours ago", hours) % {
            "hours": hours,
        }
    if diff < timedelta(days=2):
        return _("yesterday")
    if diff < timedelta(days=65):
        days = diff.days
        return ngettext("%(days)d day ago", "%(days)d days ago", days) % {
            "days": days,
        }
    if diff < timedelta(days=365):
        months = diff.days // 30
        return ngettext("%(months)d month ago", "%(months)d months ago", months) % {
            "months": months,
        }
    if diff < timedelta(days=365 * 4):
        years = diff.days // 365
        return ngettext("%(years)d year ago", "%(years)d years ago", years) % {
            "years": years,
        }
    return dt.strftime("%b %d, %Y")


def _timeago_short(diff: timedelta, dt) -> str:
    """Format timedelta as compact relative time string."""
    from starlette_babel import gettext_lazy as _

    ngettext = _
    if diff < timedelta(seconds=60):
        return ngettext("just now", "just now", 1)
    if diff < timedelta(minutes=60):
        minutes = diff.seconds // 60
        return ngettext("%(minutes)dm ago", "%(minutes)dm ago", minutes) % {
            "minutes": minutes,
        }
    if diff < timedelta(days=1):
        hours = diff.seconds // 3600
        return ngettext("%(hours)dh ago", "%(hours)dh ago", hours) % {"hours": hours}
    if diff < timedelta(days=2):
        return ngettext("%(days)dd ago", "%(days)dd ago", 1) % {"days": 1}
    if diff < timedelta(days=7):
        days = diff.days
        return ngettext("%(days)dd ago", "%(days)dd ago", days) % {"days": days}
    if diff < timedelta(days=30):
        weeks = diff.days // 7
        return ngettext("%(weeks)dw ago", "%(weeks)dw ago", weeks) % {"weeks": weeks}
    if diff < timedelta(days=365):
        months = diff.days // 30
        return ngettext("%(months)dmo ago", "%(months)dmo ago", months) % {
            "months": months,
        }
    if diff < timedelta(days=365 * 4):
        years = diff.days // 365
        return ngettext("%(years)dy ago", "%(years)dy ago", years) % {"years": years}
    return dt.strftime("%b %d, %Y")


def timeago(dt, short: bool = False):
    """Converts a datetime object to a human-readable string representing the time elapsed since the given datetime.

    Args:
        dt (datetime): The datetime object to convert.
        short (bool): If True, use compact format like "5m ago" instead of "5 minutes ago".

    Returns:
        str: A human-readable string representing the time elapsed since the given datetime,
        such as "X seconds ago", "X minutes ago", "X hours ago", "yesterday", "X days ago",
        "X months ago", or "X years ago". If the datetime is more than 4 years old,
        it returns the date in the format "MMM DD, YYYY".

        In short format, returns compact strings like "just now", "5m ago", "2h ago", etc.

    """
    try:
        diff = age_in_timedelta(dt)
        if short:
            return _timeago_short(diff, dt)
        return _timeago_verbose(diff, dt)
    except Exception:
        return ""


def format_date(dt):
    """Formats a datetime object to display only the date.

    Args:
        dt (datetime): The datetime object to format.

    Returns:
        str: A formatted date string in the format "Month DD, YYYY" (e.g., "January 15, 2024").
        Returns empty string if dt is None.
    """
    if dt is None:
        return ""
    try:
        return dt.strftime("%B %d, %Y")
    except Exception:
        return ""


def format_datetime(dt):
    """Formats a datetime object to display date and time without seconds.

    Args:
        dt (datetime): The datetime object to format.

    Returns:
        str: A formatted datetime string in the format "Month DD, YYYY at HH:MM AM/PM"
        (e.g., "January 15, 2024 at 3:45 PM"). Returns empty string if dt is None.
    """
    if dt is None:
        return ""
    try:
        return dt.strftime("%B %d, %Y at %I:%M %p")
    except Exception:
        return ""


# Add your functions here
def format_duration(seconds):
    """Formats duration in seconds to user-friendly format with rounding.

    Args:
        seconds (float): Duration in seconds.

    Returns:
        str: For 0-45 seconds, shows "x sec" (e.g., "30 sec").
        For 46 seconds to 1:45, shows "1 min".
        For 1:46 to 2:45, shows "2 min", etc.
        Returns empty string if seconds is None or invalid.
    """
    if seconds is None:
        return ""
    try:
        total_seconds = int(float(seconds))

        if total_seconds <= 45:
            return f"{total_seconds} sec"
        else:
            # Round to nearest minute for times > 45 seconds
            # 46-105 seconds = 1 min, 106-165 seconds = 2 min, etc.
            minutes = round(total_seconds / 60)
            return f"{minutes} min"
    except (ValueError, TypeError):
        return ""


def lang_url_for(request: Request, name: str, **path_params) -> str:
    """Generate language-prefixed URL for SEO routes.

    Uses the current request's language to prefix the URL generated by url_for.

    Args:
        request: FastAPI Request object
        name: Route name to generate URL for
        **path_params: Path parameters for the route

    Returns:
        str: Language-prefixed URL path (e.g., "/ca/dashboard")

    Example:
        {{ lang_url_for(request, "privacy") }}  -> "/ca/privacy"
        {{ lang_url_for(request, "user", user_id=123) }}  -> "/ca/users/123"
    """
    base_url = request.url_for(name, **path_params).path
    lang = request.state.language
    return f"/{lang}{base_url}"


def url_for_language(request: Request, lang: str, name: str, **path_params) -> str:
    """Generate URL for a specific language.

    Unlike lang_url_for which uses the current request's language, this function
    allows specifying the target language explicitly. Useful for language switchers.

    Args:
        request: FastAPI Request object
        lang: Target language code (e.g., "en", "ca", "es")
        name: Route name to generate URL for
        **path_params: Path parameters for the route

    Returns:
        str: Language-prefixed URL path (e.g., "/es/dashboard")

    Example:
        {{ url_for_language(request, "es", "privacy") }}  -> "/es/privacy"
        {{ url_for_language(request, "ca", "user", user_id=123) }}  -> "/ca/users/123"
    """
    base_url = request.url_for(name, **path_params).path
    return f"/{lang}{base_url}"


def hreflang_tags(
    request: Request, supported_languages: set[str], default_lang: str
) -> str:
    """Generate hreflang link tags for SEO.

    Creates <link rel="alternate"> tags for all supported languages plus x-default.
    Used in <head> section to help search engines understand language variants.

    Args:
        request: FastAPI Request object
        supported_languages: Set of supported language codes (e.g., {"en", "ca", "es"})
        default_lang: Default language code for x-default tag

    Returns:
        str: HTML string with hreflang link tags, one per line

    Example:
        {{ hreflang_tags(request, supported_languages, default_language)|safe }}
    """
    path = request.url.path

    # If accessed with lang prefix, get the base path
    if hasattr(request.state, "lang_prefix"):
        path = request.state.original_path
        # Remove the language prefix to get base path
        parts = path.strip("/").split("/", 1)
        if parts and len(parts[0]) == 2:
            path = "/" + parts[1] if len(parts) > 1 else "/"

    base_url = str(request.base_url).rstrip("/")

    tags = []
    for lang in sorted(supported_languages):
        url = f"{base_url}/{lang}{path}"
        tags.append(f'<link rel="alternate" hreflang="{lang}" href="{url}" />')

    # x-default points to UNPREFIXED URL (serves default/detected language)
    default_url = f"{base_url}{path}"
    tags.append(f'<link rel="alternate" hreflang="x-default" href="{default_url}" />')

    return "\n".join(tags)


templates: Jinja2Templates = Jinja2Templates(directory=frontend_templates)
jinja_env = templates.env


def render_template(
    template: str,
    request: Request,
    ctx: dict[str, Any] | None = None,
    **kwargs: Any,
) -> HTMLResponse:
    """Render a Jinja2 template and return an HTMLResponse.

    The template search path already includes the ``templates/frontend/``
    directory, so template names should be **relative to that directory**.

    Args:
        template: Path to template file relative to ``templates/frontend/``.
            Use ``"blog/list.html.jinja"``, **not** ``"frontend/blog/list.html.jinja"``.
        request: FastAPI Request object.
        ctx: Optional context dictionary merged into the template context.
        **kwargs: Extra keyword arguments forwarded to ``TemplateResponse``.

    Returns:
        HTMLResponse with the rendered template.

    Example::

        # Correct - path is relative to templates/frontend/
        render_template("blog/list.html.jinja", request)
        render_template("admin/dashboard.html.jinja", request, {"stats": stats})

        # Wrong - "frontend/" prefix is redundant and will cause a TemplateNotFound error
        render_template("frontend/blog/list.html.jinja", request)  # TemplateNotFound!
    """
    _ensure_custom_filters()
    ctx = ctx or {}
    language = getattr(request.state, "language", data_ctx.default_language)
    with _context_lock:
        globals_snapshot = dict(_template_globals)
    merged_ctx = {
        **data_ctx.model_dump(),
        **globals_snapshot,
        **_collect_provider_context(request=request),
        "request": request,
        "language": language,
        **ctx,
    }

    return templates.TemplateResponse(template, merged_ctx, **kwargs)


def render_template_string(
    template: str,
    request: Request,
    ctx: dict[str, Any] | None = None,
) -> str:
    """Render a template to a string instead of HTMLResponse.

    Useful for Server-Sent Events (SSE), AJAX responses, or any case where you need
    the rendered HTML as a string rather than a full HTTP response.

    Args:
        template: Path to template file (e.g., "admin/partials/episode.html.jinja")
        request: FastAPI Request object
        ctx: Optional context dictionary to pass to template

    Returns:
        str: Rendered template as a string

    Example:
        html = render_template_string(
            "admin/partials/episode_article.html.jinja",
            request,
            {"episode": episode}
        )
    """
    _ensure_custom_filters()
    ctx = ctx or {}
    language = getattr(request.state, "language", data_ctx.default_language)
    with _context_lock:
        globals_snapshot = dict(_template_globals)
    merged_ctx = {
        **data_ctx.model_dump(),
        **globals_snapshot,
        **_collect_provider_context(request=request),
        "request": request,
        "language": language,
        **ctx,
    }

    template_obj = templates.get_template(template)
    return template_obj.render(merged_ctx)


def render_template_stream(
    template: str,
    request: Request,
    ctx: dict[str, Any] | None = None,
) -> StreamingResponse:
    """Render a template as a streaming HTML response.

    Uses Jinja2's ``generate_async()`` to yield HTML chunks as the template
    renders, allowing the browser to start painting before the full page is
    ready.  This improves time-to-first-byte (TTFB) for large pages like
    dashboards and data tables.

    Context merging (globals, providers, etc.) works identically to
    ``render_template()``.

    Args:
        template: Path to template file relative to ``templates/frontend/``.
        request: FastAPI Request object.
        ctx: Optional context dictionary merged into the template context.

    Returns:
        StreamingResponse with ``media_type="text/html"``.

    Example::

        @router.get("/dashboard")
        async def dashboard(request: Request):
            data = await get_dashboard_data()
            return render_template_stream(
                "dashboard.html.jinja", request, {"data": data}
            )

    Note:
        HTMX partial responses are typically small and don't benefit from
        streaming.  Use this for full page loads where the ``<head>`` and
        initial layout should reach the browser as early as possible.
    """
    _ensure_custom_filters()
    ctx = ctx or {}
    language = getattr(request.state, "language", data_ctx.default_language)
    with _context_lock:
        globals_snapshot = dict(_template_globals)
    merged_ctx = {
        **data_ctx.model_dump(),
        **globals_snapshot,
        **_collect_provider_context(request=request),
        "request": request,
        "language": language,
        **ctx,
    }

    template_obj = templates.get_template(template)

    def _generate():
        yield from template_obj.generate(**merged_ctx)

    return StreamingResponse(_generate(), media_type="text/html")


def _build_merged_ctx(
    request: Request, ctx: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Build the merged template context (shared by all render functions)."""
    _ensure_custom_filters()
    ctx = ctx or {}
    language = getattr(request.state, "language", data_ctx.default_language)
    with _context_lock:
        globals_snapshot = dict(_template_globals)
    return {
        **data_ctx.model_dump(),
        **globals_snapshot,
        **_collect_provider_context(request=request),
        "request": request,
        "language": language,
        **ctx,
    }


def render_template_block(
    template: str,
    block_name: str,
    request: Request,
    ctx: dict[str, Any] | None = None,
) -> HTMLResponse:
    """Render a single named ``{% block %}`` from a template.

    Enables one template to serve both full-page and HTMX partial responses
    without duplicating markup in separate template files.

    Args:
        template: Path to template file relative to ``templates/frontend/``.
        block_name: Name of the ``{% block %}`` to render.
        request: FastAPI Request object.
        ctx: Optional context dictionary merged into the template context.

    Returns:
        HTMLResponse containing only the rendered block content.

    Raises:
        ValueError: If the named block does not exist in the template.

    Example::

        @router.get("/items")
        async def list_items(request: Request):
            items = await Item.find_all().to_list()
            ctx = {"items": items}

            if request.state.htmx:
                return render_template_block(
                    "items/list.html.jinja", "items_list", request, ctx
                )

            return render_template("items/list.html.jinja", request, ctx)
    """
    merged_ctx = _build_merged_ctx(request, ctx)
    template_obj = templates.get_template(template)

    if block_name not in template_obj.blocks:
        raise ValueError(
            f"Block '{block_name}' not found in template '{template}'. "
            f"Available blocks: {list(template_obj.blocks.keys())}"
        )

    block_func = template_obj.blocks[block_name]
    rendered = "".join(block_func(template_obj.new_context(merged_ctx)))
    return HTMLResponse(rendered)


def render_template_blocks(
    template: str,
    block_names: list[str],
    request: Request,
    ctx: dict[str, Any] | None = None,
) -> HTMLResponse:
    """Render multiple named blocks from a template, concatenated.

    Useful for HTMX out-of-band (OOB) swaps where one server response updates
    multiple parts of the page simultaneously.

    Args:
        template: Path to template file relative to ``templates/frontend/``.
        block_names: List of ``{% block %}`` names to render.
        request: FastAPI Request object.
        ctx: Optional context dictionary merged into the template context.

    Returns:
        HTMLResponse containing all rendered blocks concatenated together.

    Raises:
        ValueError: If any named block does not exist in the template.

    Example::

        @router.post("/items")
        async def create_item(request: Request):
            item = await Item.insert(...)
            items = await Item.find_all().to_list()
            ctx = {"items": items, "item_count": len(items)}

            return render_template_blocks(
                "items/list.html.jinja",
                ["items_list", "notification_badge"],
                request, ctx,
            )
    """
    merged_ctx = _build_merged_ctx(request, ctx)
    template_obj = templates.get_template(template)

    parts: list[str] = []
    for block_name in block_names:
        if block_name not in template_obj.blocks:
            raise ValueError(
                f"Block '{block_name}' not found in template '{template}'. "
                f"Available blocks: {list(template_obj.blocks.keys())}"
            )
        block_func = template_obj.blocks[block_name]
        parts.append("".join(block_func(template_obj.new_context(merged_ctx))))

    return HTMLResponse("".join(parts))


# Built-in context provider for date/time template globals
def _datetime_context() -> dict[str, Any]:
    """Provide ``now`` and ``today`` in every template context."""
    return {
        "now": datetime.now(timezone.utc),
        "today": date.today().isoformat(),
    }


register_context_provider(_datetime_context)


def _csp_nonce_context(request: Request) -> dict[str, Any]:
    """Expose the CSP nonce so templates can use it for ``<style>`` tags or other elements."""
    return {"csp_nonce": getattr(request.state, "csp_nonce", "")}


register_context_provider(_csp_nonce_context)

# Global Vars
jinja_env.globals.update({"DEBUG": data_ctx.DEBUG})

# Language URL helpers for SEO
jinja_env.globals.update({"lang_url_for": lang_url_for})
jinja_env.globals.update({"url_for_language": url_for_language})
jinja_env.globals.update({"hreflang_tags": hreflang_tags})

# Date Filters
jinja_env.filters["timeago"] = timeago
jinja_env.filters["format_date"] = format_date
jinja_env.filters["format_datetime"] = format_datetime

# Duration Filters
jinja_env.filters["format_duration"] = format_duration
jinja_env.filters["duration"] = format_duration

# Lazy registration of i18n filters, user-defined filters, and hotreload global
_custom_filters_registered = False


def _ensure_custom_filters() -> None:
    """Register custom template filters and hotreload global on first use."""
    global _custom_filters_registered
    if _custom_filters_registered:
        return
    _custom_filters_registered = True

    # Configure Jinja environment with starlette-babel i18n filters (deferred)
    from starlette_babel.contrib.jinja import configure_jinja_env

    configure_jinja_env(jinja_env)

    # Hotreload is imported lazily to avoid pulling in vibetuner.frontend
    from vibetuner.frontend.hotreload import hotreload

    jinja_env.globals.update({"hotreload": hotreload})

    app_config = load_app_config()
    builtin_filters = set(jinja_env.filters.keys())

    for filter_name, filter_func in app_config.template_filters.items():
        if filter_name in builtin_filters:
            logger.warning(
                f"Custom filter '{filter_name}' overrides built-in filter. "
                "Consider using a different name to avoid confusion."
            )
        try:
            if not callable(filter_func):
                logger.error(
                    f"Template filter '{filter_name}' is not callable, skipping"
                )
                continue
            jinja_env.filters[filter_name] = filter_func
            logger.debug(f"Registered custom filter: {filter_name}")
        except Exception as e:
            logger.error(f"Failed to register template filter '{filter_name}': {e}")
