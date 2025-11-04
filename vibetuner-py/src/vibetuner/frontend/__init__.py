from typing import Any

from fastapi import APIRouter, Depends as Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from vibetuner import paths

from .deps import LangDep as LangDep, MagicCookieDep as MagicCookieDep
from .lifespan import ctx, lifespan
from .middleware import middlewares
from .routes import auth, debug, health, language, meta, user
from .templates import render_template


_registered_routers: list[APIRouter] = []


def register_router(router: APIRouter) -> None:
    _registered_routers.append(router)


try:
    import app.frontend.oauth as _app_oauth  # noqa: F401  # type: ignore[unresolved-import]
    import app.frontend.routes as _app_routes  # noqa: F401  # type: ignore[unresolved-import]

    # Register OAuth routes after providers are registered
    from .routes.auth import register_oauth_routes

    register_oauth_routes()
except (ImportError, ModuleNotFoundError):
    pass


dependencies: list[Any] = [
    # Add any dependencies that should be available globally
]

app = FastAPI(
    debug=ctx.DEBUG,
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    middleware=middlewares,
    dependencies=dependencies,
)

# Static files
app.mount(f"/static/v{ctx.v_hash}/css", StaticFiles(directory=paths.css), name="css")
app.mount(f"/static/v{ctx.v_hash}/img", StaticFiles(directory=paths.img), name="img")
app.mount(f"/static/v{ctx.v_hash}/js", StaticFiles(directory=paths.js), name="js")

app.mount("/static/favicons", StaticFiles(directory=paths.favicons), name="favicons")


@app.get("/static/v{v_hash}/css/{subpath:path}", response_class=RedirectResponse)
@app.get("/static/css/{subpath:path}", response_class=RedirectResponse)
def css_redirect(request: Request, subpath: str):
    return request.url_for("css", path=subpath).path


@app.get("/static/v{v_hash}/img/{subpath:path}", response_class=RedirectResponse)
@app.get("/static/img/{subpath:path}", response_class=RedirectResponse)
def img_redirect(request: Request, subpath: str):
    return request.url_for("img", path=subpath).path


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

app.include_router(meta.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(language.router)

for router in _registered_routers:
    app.include_router(router)


@app.get("/", name="homepage", response_class=HTMLResponse)
def default_index(request: Request) -> HTMLResponse:
    return render_template("index.html.jinja", request)


app.include_router(debug.router)
app.include_router(health.router)
