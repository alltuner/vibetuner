from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from ..templates import template_render


router = APIRouter(prefix="/debug")


@router.get("/health")
def health():
    return {"ping": "ok"}


@router.get("/version", response_class=HTMLResponse)
def debug_version(request: Request):
    return template_render("debug/version.html.jinja", request)
