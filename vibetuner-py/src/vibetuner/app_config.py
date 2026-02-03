# ABOUTME: Defines VibetunerApp, the explicit configuration class for vibetuner applications.
# ABOUTME: Users create tune.py with an `app = VibetunerApp(...)` to configure their app.
from typing import Any, Callable

from beanie import Document, View
from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict
from starlette.middleware import Middleware
from typer import Typer


class VibetunerApp(BaseModel):
    """Explicit configuration for a vibetuner application.

    Create a `tune.py` file in your package root with:

        from vibetuner import VibetunerApp

        from myapp.frontend.routes import app_router
        from myapp.models import User, Post

        app = VibetunerApp(
            routes=[app_router],
            models=[User, Post],
        )

    Zero-config works out of the box. Only create tune.py when customizing.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Models (Beanie documents and views)
    models: list[type[Document] | type[View]] = []

    # Frontend
    routes: list[APIRouter] = []
    middleware: list[Middleware] = []
    template_filters: dict[str, Callable[..., Any]] = {}
    frontend_lifespan: Callable[..., Any] | None = None

    # OAuth providers (e.g., ["google", "github"])
    oauth_providers: list[str] = []

    # Worker
    tasks: list[Callable[..., Any]] = []
    worker_lifespan: Callable[..., Any] | None = None

    # CLI extensions
    cli: Typer | None = None
