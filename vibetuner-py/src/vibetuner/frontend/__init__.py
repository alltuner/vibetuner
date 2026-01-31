from typing import Any

from fastapi import APIRouter, Depends as Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

import vibetuner.frontend.lifespan as lifespan_module
from vibetuner import paths
from vibetuner.logging import logger

from .deps import (
    LangDep as LangDep,
    LangPrefixDep as LangPrefixDep,
    MagicCookieDep as MagicCookieDep,
)
from .lifespan import ctx
from .middleware import middlewares
from .routes import auth, debug, health, language, meta, user
from .routing import LocalizedRouter as LocalizedRouter, localized as localized
from .templates import (
    hreflang_tags as hreflang_tags,
    lang_url_for as lang_url_for,
    render_template,
    url_for_language as url_for_language,
)


_registered_routers: list[APIRouter] = []


def register_router(router: APIRouter) -> None:
    _registered_routers.append(router)


try:
    import app.frontend.oauth as _app_oauth  # type: ignore[unresolved-import] # noqa: F401
    import app.frontend.routes as _app_routes  # type: ignore[unresolved-import] # noqa: F401

    # Register OAuth routes after providers are registered
    from .routes.auth import register_oauth_routes

    register_oauth_routes()
except ModuleNotFoundError:
    # Silent pass for missing app.frontend.oauth or app.frontend.routes modules (expected in some projects)
    pass
except ImportError as e:
    # Log warning for any import error (including syntax errors, missing dependencies, etc.)
    logger.warning(
        f"Failed to import app.frontend.oauth or app.frontend.routes: {e}. OAuth and custom routes will not be available."
    )

try:
    from app.frontend.middleware import (
        middlewares as app_middlewares,  # type: ignore[unresolved-import]
    )

    middlewares.extend(app_middlewares)
except ModuleNotFoundError:
    pass
except ImportError as e:
    # Log warning for any import error (including syntax errors, missing dependencies, etc.)
    logger.warning(
        f"Failed to import app.frontend.middleware: {e}. Additional middlewares will not be available."
    )


dependencies: list[Any] = [
    # Add any dependencies that should be available globally
]

app = FastAPI(
    debug=ctx.DEBUG,
    lifespan=lifespan_module.lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    middleware=middlewares,
    dependencies=dependencies,
)

# Static files
if paths.css.is_dir():
    app.mount(
        f"/static/v{ctx.v_hash}/css", StaticFiles(directory=paths.css), name="css"
    )
else:
    logger.warning(
        f"CSS static directory ({paths.css}) not found; CSS files will not be served."
    )

if paths.img.is_dir():
    app.mount(
        f"/static/v{ctx.v_hash}/img", StaticFiles(directory=paths.img), name="img"
    )
else:
    logger.warning(
        f"Image static directory ({paths.img}) not found; image files will not be served."
    )
if paths.js.is_dir():
    app.mount(f"/static/v{ctx.v_hash}/js", StaticFiles(directory=paths.js), name="js")
else:
    logger.warning(
        f"JavaScript static directory ({paths.js}) not found; JS files will not be served."
    )

if paths.favicons.is_dir():
    app.mount(
        "/static/favicons", StaticFiles(directory=paths.favicons), name="favicons"
    )
else:
    logger.warning(
        f"Favicons static directory ({paths.favicons}) not found; favicon files will not be served."
    )

if paths.fonts.is_dir():
    app.mount("/static/fonts", StaticFiles(directory=paths.fonts), name="fonts")
else:
    logger.warning(
        f"Fonts static directory ({paths.fonts}) not found; font files will not be served."
    )


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


app.include_router(debug.auth_router)
app.include_router(debug.router)
app.include_router(health.router)
