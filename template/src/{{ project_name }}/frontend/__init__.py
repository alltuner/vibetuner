from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from .. import _paths as paths
from .deps import LangDep as LangDep
from .lifespan import ctx, lifespan
from .middleware import middlewares
from .routes import (
    debug,
)
from .templates import templates


__all__ = [
    "Request",
    "templates",
]

app = FastAPI(
    debug=ctx.DEBUG,
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    middleware=middlewares,
)

# Static files
app.mount(f"/static/v{ctx.v_hash}/css", StaticFiles(directory=paths.css), name="css")
app.mount(f"/static/v{ctx.v_hash}/js", StaticFiles(directory=paths.js), name="js")
app.mount("/static/favicons", StaticFiles(directory=paths.favicons), name="favicons")
app.mount("/static/img", StaticFiles(directory=paths.img), name="img")


@app.get("/static/v{v_hash}/css/{subpath:path}", response_class=RedirectResponse)
@app.get("/static/css/{subpath:path}", response_class=RedirectResponse)
def css_redirect(request: Request, subpath: str):
    return request.url_for("css", path=subpath).path


@app.get("/static/v{v_hash}/js/{subpath:path}", response_class=RedirectResponse)
@app.get("/static/js/{subpath:path}", response_class=RedirectResponse)
def js_redirect(request: Request, subpath: str):
    return request.url_for("js", path=subpath).path


if ctx.DEBUG:
    from .hotreload import hotreload

    app.add_websocket_route(
        "/hot-reload",
        route=hotreload,  # type: ignore
        name="hot-reload",
    )

app.include_router(debug.router)

# Add your routes below
# EOF
