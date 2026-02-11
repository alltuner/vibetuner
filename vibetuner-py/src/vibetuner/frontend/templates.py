# ABOUTME: Re-exports template rendering from vibetuner.rendering.
# ABOUTME: Kept for internal framework imports within the frontend package.
from vibetuner.rendering import (
    format_date,
    format_datetime,
    format_duration,
    hreflang_tags,
    lang_url_for,
    register_context_provider,
    register_globals,
    render_static_template,
    render_template,
    render_template_string,
    timeago,
    url_for_language,
)


__all__ = [
    "format_date",
    "format_datetime",
    "format_duration",
    "hreflang_tags",
    "lang_url_for",
    "register_context_provider",
    "register_globals",
    "render_static_template",
    "render_template",
    "render_template_string",
    "timeago",
    "url_for_language",
]
