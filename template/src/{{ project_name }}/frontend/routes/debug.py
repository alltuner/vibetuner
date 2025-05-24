from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from ... import __version__
from ..templates import templates


router = APIRouter(prefix="/debug")


@router.get("/health")
def health():
    return {"ping": "ok"}


@router.get("/version", response_class=HTMLResponse)
def debug_version(request: Request):
    return templates.TemplateResponse(
        "debug/version.html.jinja",
        {"request": request, "version": __version__},
    )
