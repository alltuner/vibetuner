from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse

from vibetuner.paths import fallback_static_default

from ..templates import render_template


router = APIRouter()


# Favicon Related Routes
# Todo, provide an easy way to override default statics
@router.get("/favicon.ico", response_class=FileResponse)
async def favicon() -> Path:
    return fallback_static_default("favicons", "favicon.ico")


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
