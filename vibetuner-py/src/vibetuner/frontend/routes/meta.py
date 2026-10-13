# ABOUTME: Core meta routes: favicon, robots.txt, sitemap.xml, webmanifest, browserconfig.
# ABOUTME: App routes on the same path take precedence via core_router().
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from starlette.routing import Route

from vibetuner.logging import logger
from vibetuner.paths import paths

from ..templates import render_template


router = APIRouter()


# Favicon Related Routes
# Todo, provide an easy way to override default statics
@router.get("/favicon.ico", response_class=FileResponse)
async def favicon() -> Path:
    return paths.favicons / "favicon.ico"


# Misc static routes
@router.get("/robots.txt", response_class=PlainTextResponse)
def robots(request: Request) -> HTMLResponse:
    return render_template(
        "meta/robots.txt.jinja",
        request=request,
        media_type="text/plain",
    )


@router.get("/sitemap.xml")
async def sitemap(request: Request) -> HTMLResponse:
    return render_template(
        "meta/sitemap.xml.jinja",
        request,
        media_type="application/xml",
    )


@router.get("/site.webmanifest")
async def site_webmanifest(request: Request) -> HTMLResponse:
    return render_template(
        "meta/site.webmanifest.jinja",
        request,
        media_type="application/manifest+json",
    )


@router.get("/browserconfig.xml")
async def browserconfig(request: Request) -> HTMLResponse:
    return render_template(
        "meta/browserconfig.xml.jinja",
        request,
        media_type="application/xml",
    )


def _get_paths(routers: list[APIRouter]) -> set[str]:
    return {
        route.path
        for router in routers
        for route in router.routes
        if isinstance(route, Route) and route.methods and "GET" in route.methods
    }


def core_router(app_routers: list[APIRouter]) -> APIRouter:
    """Return the core meta routes, minus any path the app serves with GET itself.

    Core routes are registered before app routes, so without this an app route
    such as a database-backed ``/sitemap.xml`` would be shadowed.
    """
    app_paths = _get_paths(app_routers)
    filtered = APIRouter()
    for route in router.routes:
        path: str | None = getattr(route, "path", None)
        if path in app_paths:
            logger.debug(f"App route overrides core meta route {path}")
            continue
        filtered.routes.append(route)
    return filtered
