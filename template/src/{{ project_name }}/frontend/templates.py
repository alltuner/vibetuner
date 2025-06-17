from typing import Any

from fastapi import Request
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse
from starlette_babel.contrib.jinja import configure_jinja_env

from .._paths import frontend_templates
from ..context import Context
from ..templates import render_template as render_static_template
from .hotreload import hotreload


__all__ = [
    "render_static_template",
]

data_ctx = Context()


# Add your functions here
# Until here

templates: Jinja2Templates = Jinja2Templates(directory=frontend_templates)
jinja_env = templates.env  # ty: ignore[possibly-unbound-attribute]


def render_template(
    template: str,
    request: Request,
    ctx: dict[str, Any] | None = None,
    **kwargs: Any,
) -> HTMLResponse:
    ctx = ctx or {}
    merged_ctx = {**data_ctx.model_dump(), "request": request, **ctx}

    return templates.TemplateResponse(template, merged_ctx, **kwargs)


# FIXME: This is kept like this for compatibility with the old codebase.
template_render = render_template

jinja_env.globals.update({"DEBUG": data_ctx.DEBUG})
jinja_env.globals.update({"hotreload": hotreload})

# Customize your templates here

# Until here
configure_jinja_env(jinja_env)
