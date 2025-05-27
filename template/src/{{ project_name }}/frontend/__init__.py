from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from .. import _paths as paths
from .deps import LangDep as LangDep
from .lifespan import ctx, lifespan
from .middleware import middlewares
from .routes import debug as debug
from .templates import templates


__all__ = [
    "Request",
    "templates",
]

app = FastAPI(
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    middleware=middlewares,
)

app.mount("/static", StaticFiles(directory=paths.statics), name="static")
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
