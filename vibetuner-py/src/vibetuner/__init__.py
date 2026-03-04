# ABOUTME: Main vibetuner package entry point.
# ABOUTME: Exports VibetunerApp, AsyncTyper, and core template rendering functions.
from vibetuner.app_config import VibetunerApp
from vibetuner.rendering import (
    register_context_provider,
    register_globals,
    render,
    render_template,
    render_template_string,
)


def __getattr__(name: str):
    if name == "AsyncTyper":
        from vibetuner.cli import AsyncTyper

        return AsyncTyper
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "AsyncTyper",
    "VibetunerApp",
    "register_context_provider",
    "register_globals",
    "render",
    "render_template",
    "render_template_string",
]
