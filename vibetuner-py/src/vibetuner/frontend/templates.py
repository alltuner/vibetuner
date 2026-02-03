from datetime import timedelta
from typing import Any

from fastapi import Request
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse
from starlette_babel import gettext_lazy as _, gettext_lazy as ngettext
from starlette_babel.contrib.jinja import configure_jinja_env

from vibetuner.context import ctx as data_ctx
from vibetuner.loader import load_app_config
from vibetuner.logging import logger
from vibetuner.paths import frontend_templates
from vibetuner.templates import render_static_template
from vibetuner.time import age_in_timedelta

from .hotreload import hotreload


__all__ = [
    "render_static_template",
    "render_template",
    "render_template_string",
    "lang_url_for",
    "url_for_language",
    "hreflang_tags",
]


def _timeago_verbose(diff: timedelta, dt) -> str:
    """Format timedelta as verbose relative time string."""
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
    _ensure_custom_filters()
    ctx = ctx or {}
    language = getattr(request.state, "language", data_ctx.default_language)
    merged_ctx = {
        **data_ctx.model_dump(),
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
    merged_ctx = {
        **data_ctx.model_dump(),
        "request": request,
        "language": language,
        **ctx,
    }

    template_obj = templates.get_template(template)
    return template_obj.render(merged_ctx)


# Global Vars
jinja_env.globals.update({"DEBUG": data_ctx.DEBUG})
jinja_env.globals.update({"hotreload": hotreload})

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

# Configure Jinja environment with built-in filters
configure_jinja_env(jinja_env)

# Lazy registration of user-defined filters to avoid circular imports when tune.py imports routes
_custom_filters_registered = False


def _ensure_custom_filters() -> None:
    """Register custom template filters from tune.py on first use."""
    global _custom_filters_registered
    if _custom_filters_registered:
        return
    _custom_filters_registered = True

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
