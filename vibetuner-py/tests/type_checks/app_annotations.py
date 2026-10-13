# ABOUTME: App-side code that `ty check` must accept when it configures VibetunerApp.
# ABOUTME: Never executed; it guards the public typing contract against regressions.
from collections.abc import Callable

from beanie import Document, View
from fastapi import APIRouter
from markupsafe import Markup, escape
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from vibetuner import VibetunerApp
from vibetuner.provider import OauthProviderModel


class Artwork(Document):
    title: str


class SqlArtwork:
    pass


class AppRouter(APIRouter):
    pass


class NoopMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        return await call_next(request)


def markdown(text: str) -> Markup:
    return escape(text)


async def send_digest(user_id: str) -> None:
    pass


APP_MODELS: list[type[Document] | type[View]] = [Artwork]
APP_SQL_MODELS: list[type[SqlArtwork]] = [SqlArtwork]
APP_ROUTES: list[AppRouter] = [AppRouter()]
APP_MIDDLEWARE = [Middleware(NoopMiddleware)]
TEMPLATE_FILTERS = {"markdown": markdown}
OAUTH_PROVIDERS: tuple[str, ...] = ("google",)
CUSTOM_OAUTH_PROVIDERS: dict[str, OauthProviderModel] = {}
TASKS: list[Callable[[str], object]] = [send_digest]
RUNTIME_CONFIG: dict[str, dict[str, str]] = {}

app = VibetunerApp(
    models=APP_MODELS,
    sql_models=APP_SQL_MODELS,
    routes=APP_ROUTES,
    api_routes=APP_ROUTES,
    middleware=APP_MIDDLEWARE,
    template_filters=TEMPLATE_FILTERS,
    oauth_providers=OAUTH_PROVIDERS,
    custom_oauth_providers=CUSTOM_OAUTH_PROVIDERS,
    tasks=TASKS,
    runtime_config=RUNTIME_CONFIG,
)
