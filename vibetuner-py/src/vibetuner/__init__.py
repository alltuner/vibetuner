# ABOUTME: Main vibetuner package entry point.
# ABOUTME: Exports VibetunerApp, AsyncTyper, render functions, SSE, CRUD, and HTMX helpers.
from importlib.metadata import version

from vibetuner.app_config import VibetunerApp
from vibetuner.crud import create_crud_routes
from vibetuner.frontend.deps import require_htmx
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
from vibetuner.sse import broadcast, sse_endpoint
from vibetuner.theming import register_tenant_theme_provider


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
    "broadcast",
    "create_crud_routes",
    "register_context_provider",
    "register_globals",
    "register_tenant_theme_provider",
    "render",
    "render_template",
    "render_template_block",
    "render_template_blocks",
    "render_template_stream",
    "render_template_string",
    "require_htmx",
    "sse_endpoint",
]
