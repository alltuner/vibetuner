from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from .. import _paths as paths
from .lifespan import lifespan
from .middleware import middlewares
from .routes import debug as debug
from .templates import templates


__all__ = [
    "HTTPException",
    "Request",
    "Response",
    "HTMLResponse",
    "JSONResponse",
    "RedirectResponse",
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
app.include_router(debug.router)

# Add your routes below
# EOF
