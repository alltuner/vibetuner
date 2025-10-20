from datetime import timedelta
from typing import Any

from fastapi import Request
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse
from starlette_babel import gettext_lazy as _, gettext_lazy as ngettext
from starlette_babel.contrib.jinja import configure_jinja_env

from vibetuner.context import Context
from vibetuner.paths import frontend_templates
from vibetuner.templates import render_static_template
from vibetuner.time import age_in_timedelta

from .hotreload import hotreload


__all__ = [
    "render_static_template",
]

data_ctx = Context()


def timeago(dt):
    """Converts a datetime object to a human-readable string representing the time elapsed since the given datetime.

    Args:
        dt (datetime): The datetime object to convert.

    Returns:
        str: A human-readable string representing the time elapsed since the given datetime,
        such as "X seconds ago", "X minutes ago", "X hours ago", "yesterday", "X days ago",
        "X months ago", or "X years ago". If the datetime is more than 4 years old,
        it returns the date in the format "MMM DD, YYYY".

    """
    try:
        diff = age_in_timedelta(dt)

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


templates: Jinja2Templates = Jinja2Templates(directory=frontend_templates)
jinja_env = templates.env


def render_template(
    template: str,
    request: Request,
    ctx: dict[str, Any] | None = None,
    **kwargs: Any,
) -> HTMLResponse:
    ctx = ctx or {}
    merged_ctx = {**data_ctx.model_dump(), "request": request, **ctx}

    return templates.TemplateResponse(template, merged_ctx, **kwargs)


# Global Vars
jinja_env.globals.update({"DEBUG": data_ctx.DEBUG})
jinja_env.globals.update({"hotreload": hotreload})

# Date Filters
jinja_env.filters["timeago"] = timeago
jinja_env.filters["format_date"] = format_date
jinja_env.filters["format_datetime"] = format_datetime

# Duration Filters
jinja_env.filters["format_duration"] = format_duration
jinja_env.filters["duration"] = format_duration

configure_jinja_env(jinja_env)
