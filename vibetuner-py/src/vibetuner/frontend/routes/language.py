from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ..deps import require_htmx
from ..templates import render_template


router = APIRouter()


@router.get("/set-language/{lang}")
async def set_language(request: Request, lang: str, current: str) -> RedirectResponse:
    new_url = f"/{lang}{current[3:]}" if current else request.url_for("homepage").path
    response = RedirectResponse(url=new_url)
    response.set_cookie(key="language", value=lang, max_age=31536000)

    return response


@router.get("/get-languages", dependencies=[Depends(require_htmx)])
async def get_languages(request: Request) -> HTMLResponse:
    """Return a list of supported languages."""
    return render_template(
        "lang/select.html.jinja",
        request=request,
        ctx={"current_language": request.state.language},
    )
