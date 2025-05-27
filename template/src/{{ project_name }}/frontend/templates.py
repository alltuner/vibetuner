from typing import Any

from fastapi import Request
from fastapi.templating import Jinja2Templates
from starlette_babel.contrib.jinja import configure_jinja_env

from .._context import ctx_dict
from .._paths import templates as template_path


# Add your functions here
# Until here

templates = Jinja2Templates(directory=template_path)


def template_render(
    template: str,
    request: Request,
    ctx: dict[str, Any] | None = None,
):
    ctx = ctx or {}
    merged_ctx = {**ctx_dict, "request": request, **ctx}

    return templates.TemplateResponse(template, merged_ctx)


templates.env.globals.update({"DEBUG": ctx.DEBUG})
templates.env.globals.update({"hotreload": hotreload})

# Customize your templates here
# Until here
configure_jinja_env(templates.env)
