from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .. import STATICS_DIR
from .lifespan import ctx, lifespan
from .middleware import middlewares
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


@app.get("/debug/test", response_class=HTMLResponse)
def debug_test(request: Request):
    """This route indicates the app works correctly."""
    return templates.TemplateResponse(
        request=request, name="item.html", context={"id": id}
    )


# Add your routes below
# EOF
