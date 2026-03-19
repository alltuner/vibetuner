# ABOUTME: Main vibetuner package entry point.
# ABOUTME: Exports VibetunerApp, AsyncTyper, and core template rendering functions.
from importlib.metadata import version

from vibetuner.app_config import VibetunerApp
from vibetuner.rendering import (
    register_context_provider,
    register_globals,
    render,
    render_template,
    render_template_block,
    render_template_blocks,
    render_template_stream,
    render_template_string,
)


__version__ = version("vibetuner")


def __getattr__(name: str):
    if name == "AsyncTyper":
        from vibetuner.cli import AsyncTyper

        return AsyncTyper
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "__version__",
    "AsyncTyper",
    "VibetunerApp",
    "register_context_provider",
    "register_globals",
    "render",
    "render_template",
    "render_template_block",
    "render_template_blocks",
    "render_template_stream",
    "render_template_string",
]
