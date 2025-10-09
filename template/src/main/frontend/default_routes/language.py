from babel import Locale
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ..deps import require_htmx
from ..lifespan import ctx
from ..templates import render_template


router = APIRouter()

LOCALE_NAMES: dict[str, str] = dict(
    sorted(
        {
            locale: (Locale.parse(locale).display_name or locale).capitalize()
            for locale in ctx.supported_languages
        }.items(),
        key=lambda x: x[1],
    ),
)


@router.get("/set-language/{lang}")
async def set_language(request: Request, lang: str, current: str) -> RedirectResponse:
    new_url = f"/{lang}{current[3:]}" if current else request.url_for("homepage").path
    response = RedirectResponse(url=new_url)
    response.set_cookie(key="language", value=lang, max_age=3600)

    return response


@router.get("/get-languages", dependencies=[Depends(require_htmx)])
async def get_languages(request: Request) -> HTMLResponse:
    """Return a list of supported languages."""

    return render_template(
        "lang/select.html.jinja",
        request=request,
        ctx={
            "locale_names": LOCALE_NAMES,
            "current_language": request.state.language,
        },
    )
