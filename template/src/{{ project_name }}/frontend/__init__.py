from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .._config import STATICS_DIR
from .lifespan import ctx, lifespan
from .templates import jinja

app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory=STATICS_DIR), name="static")


@app.get("/")
@jinja.page("index.html")
def index() -> None:
    print(ctx.version)
    """This route serves the index.html template."""
    ...


# Add your routes below
# EOF
