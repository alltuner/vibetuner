from typing import Annotated, Optional

from fastapi import Depends, HTTPException, Request


async def require_htmx(request: Request) -> None:
    if not request.state.htmx:
        raise HTTPException(status_code=400, detail="HTMX header not found")


async def enforce_lang(request: Request, lang: Optional[str] = None):
    if lang is None or lang != request.state.language:
        redirect_url = request.url_for(
            request.scope["endpoint"].__name__,
            **{**request.path_params, "lang": request.state.language},
        ).path
        raise HTTPException(
            status_code=307,
            detail=f"Redirecting to canonical language: {request.state.language}",
            headers={"Location": redirect_url},
        )

    return request.state.language


LangDep = Annotated[str, Depends(enforce_lang)]


MAGIC_COOKIE_NAME = "magic_access"


def require_magic_cookie(request: Request) -> None:
    """Dependency to check if the magic access cookie is present."""
    if MAGIC_COOKIE_NAME not in request.cookies:
        raise HTTPException(status_code=403, detail="Access forbidden")

    if request.cookies[MAGIC_COOKIE_NAME] != "granted":
        raise HTTPException(status_code=403, detail="Access forbidden")


MagicCookieDep = Depends(require_magic_cookie)
