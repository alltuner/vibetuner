# ABOUTME: FastAPI application factory for vibetuner frontend.
# ABOUTME: Loads user config from tune.py and wires routes, middleware, etc.
from typing import Any

from fastapi import Depends as Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

import vibetuner.frontend.lifespan as lifespan_module
from vibetuner.loader import load_app_config
from vibetuner.logging import logger
from vibetuner.paths import paths

from .lifespan import ctx
from .middleware import middlewares
from .oauth import auto_register_providers
from .routes import auth, debug, health, language, meta, user
from .routes.auth import register_oauth_routes
from .routing import LocalizedRouter as LocalizedRouter, localized as localized
from .templates import render_template


# Load user's app configuration
_app_config = load_app_config()

# Add user middleware to the list (before app creation)
for mw in _app_config.middleware:
    middlewares.append(mw)

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
app.mount(f"/static/v{ctx.v_hash}/css", StaticFiles(directory=paths.css), name="css")
app.mount(f"/static/v{ctx.v_hash}/img", StaticFiles(directory=paths.img), name="img")
app.mount(f"/static/v{ctx.v_hash}/js", StaticFiles(directory=paths.js), name="js")

app.mount("/static/favicons", StaticFiles(directory=paths.favicons), name="favicons")
app.mount("/static/fonts", StaticFiles(directory=paths.fonts), name="fonts")


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

# Auto-register OAuth providers from config + env vars
auto_register_providers(_app_config.oauth_providers, _app_config.custom_oauth_providers)

# Register OAuth routes on auth.router (must happen before include_router)
register_oauth_routes()

# Core routes
app.include_router(meta.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(language.router)

# User routes from tune.py
for router in _app_config.routes:
    app.include_router(router)
    logger.debug(f"Registered user router: {router}")


@app.get("/", name="homepage", response_class=HTMLResponse)
def default_index(request: Request) -> HTMLResponse:
    return render_template("index.html.jinja", request)


# Debug and health routes (always last)
app.include_router(debug.auth_router)
app.include_router(debug.router)
app.include_router(health.router)
