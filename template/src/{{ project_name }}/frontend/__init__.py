from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .. import STATICS_DIR
from .lifespan import ctx, lifespan
from .middleware import middlewares
from .routes import debug as debug
from .templates import templates


__all__ = [
    "HTTPException",
    "Request",
    "Response",
    "HTMLResponse",
    "ctx",
    "templates",
]

app = FastAPI(
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    middleware=middlewares,
)
app.mount("/static", StaticFiles(directory=STATICS_DIR), name="static")
app.include_router(debug.router)

# Add your routes below
# EOF
