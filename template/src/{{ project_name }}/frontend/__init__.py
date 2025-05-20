from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .. import STATICS_DIR
from .lifespan import ctx, lifespan
from .templates import jinja, templates


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory=STATICS_DIR), name="static")


@app.get("/")
@jinja.page("index.html")
def index() -> None:
    """This route serves the index.html template."""
    ...


# Add your routes below
# EOF
