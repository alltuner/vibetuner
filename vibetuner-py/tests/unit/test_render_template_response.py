# ABOUTME: Renders a real Jinja template through render_template to check the response
# ABOUTME: is built with Starlette's current TemplateResponse(request, name, ...) signature.
# ruff: noqa: S101
import warnings
from typing import Any
from unittest.mock import patch

from jinja2 import DictLoader, Environment
from starlette.requests import Request
from starlette.templating import Jinja2Templates


def _build_ctx(request: Request, ctx: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"request": request, **(ctx or {})}


def test_render_template_emits_no_deprecation_warning() -> None:
    from vibetuner.rendering import render_template

    env = Environment(
        loader=DictLoader({"page.html.jinja": "<h1>{{ title }}</h1>"}),
        autoescape=True,
    )
    request = Request({"type": "http", "method": "GET", "path": "/", "headers": []})

    with (
        patch("vibetuner.rendering.templates", Jinja2Templates(env=env)),
        patch("vibetuner.rendering._build_merged_ctx", side_effect=_build_ctx),
        warnings.catch_warnings(),
    ):
        warnings.simplefilter("error", DeprecationWarning)
        response = render_template(
            "page.html.jinja",
            request,
            {"title": "Hi"},
            status_code=201,
            headers={"x-test": "1"},
        )

    assert response.status_code == 201
    assert response.headers["x-test"] == "1"
    assert response.body == b"<h1>Hi</h1>"
