# ABOUTME: Tests for the core meta routes (robots.txt, sitemap.xml, favicon, ...).
# ABOUTME: Verifies app routes on the same path and method take precedence over core ones.

# ruff: noqa: S101
from fastapi import APIRouter, FastAPI
from fastapi.responses import PlainTextResponse
from fastapi.testclient import TestClient
from starlette.routing import Route
from vibetuner.frontend.routes import meta


def _get_paths(router: APIRouter) -> set[str]:
    return {
        route.path
        for route in router.routes
        if isinstance(route, Route) and route.methods and "GET" in route.methods
    }


def test_app_route_overrides_core_sitemap() -> None:
    app_router = APIRouter()

    @app_router.get("/sitemap.xml", response_class=PlainTextResponse)
    async def app_sitemap() -> str:
        return "app sitemap"

    app = FastAPI()
    # Same order as vibetuner.frontend.application: core meta routes first.
    app.include_router(meta.core_router([app_router]))
    app.include_router(app_router)

    response = TestClient(app).get("/sitemap.xml")

    assert response.status_code == 200
    assert response.text == "app sitemap"


def test_api_route_overrides_core_route() -> None:
    api_router = APIRouter()

    @api_router.get("/robots.txt")
    async def app_robots() -> str:
        return "app robots"

    assert "/robots.txt" not in _get_paths(meta.core_router([APIRouter(), api_router]))


def test_core_routes_kept_when_not_overridden() -> None:
    app_router = APIRouter()

    @app_router.get("/sitemap.xml")
    async def app_sitemap() -> str:
        return "app sitemap"

    paths = _get_paths(meta.core_router([app_router]))

    assert "/sitemap.xml" not in paths
    assert {
        "/robots.txt",
        "/favicon.ico",
        "/site.webmanifest",
        "/browserconfig.xml",
    } <= paths


def test_non_get_route_does_not_override_core_route() -> None:
    app_router = APIRouter()

    @app_router.post("/sitemap.xml")
    async def ping_sitemap() -> None:
        return None

    assert "/sitemap.xml" in _get_paths(meta.core_router([app_router]))


def test_core_router_does_not_mutate_module_router() -> None:
    app_router = APIRouter()

    @app_router.get("/sitemap.xml")
    async def app_sitemap() -> str:
        return "app sitemap"

    meta.core_router([app_router])

    assert "/sitemap.xml" in _get_paths(meta.router)
