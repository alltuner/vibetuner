from typing import Any

from fastapi import Request
from fastapi.templating import Jinja2Templates
from starlette_babel.contrib.jinja import configure_jinja_env

from .._context import data_ctx
from .._paths import templates as template_path
from .hotreload import hotreload


# Add your functions here
# Until here

templates: Jinja2Templates = Jinja2Templates(directory=template_path)
jinja_env = templates.env  # ty: ignore[possibly-unbound-attribute]


def template_render(
    template: str, request: Request, ctx: dict[str, Any] | None = None, **kwargs: Any
):
    ctx = ctx or {}
    merged_ctx = {**data_ctx.model_dump(), "request": request, **ctx}

    return templates.TemplateResponse(template, merged_ctx, **kwargs)


jinja_env.globals.update({"DEBUG": data_ctx.DEBUG})
jinja_env.globals.update({"hotreload": hotreload})

# Customize your templates here

# Until here
configure_jinja_env(jinja_env)
