from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from vibetuner.context import ctx

from ..deps import require_htmx
from ..templates import render_template


# Cookie expiry: 1 year in seconds
LANGUAGE_COOKIE_MAX_AGE = 365 * 24 * 60 * 60  # 31536000

router = APIRouter()


@router.get("/set-language/{lang}")
async def set_language(request: Request, lang: str, current: str) -> RedirectResponse:
    # Validate language is supported
    if lang not in ctx.supported_languages:
        raise HTTPException(status_code=400, detail="Unsupported language")

    # Validate current URL is an internal path (prevent open redirect)
    # Must start with /{lang}/ pattern and be a relative path
    if current:
        # Strip the language prefix from current URL
        parts = current.strip("/").split("/", 1)
        if parts and len(parts[0]) == 2 and parts[0].isalpha():
            base_path = "/" + parts[1] if len(parts) > 1 else "/"
        else:
            base_path = current if current.startswith("/") else f"/{current}"
        new_url = f"/{lang}{base_path}"
    else:
        new_url = request.url_for("homepage").path

    response = RedirectResponse(url=new_url)
    response.set_cookie(key="language", value=lang, max_age=LANGUAGE_COOKIE_MAX_AGE)

    return response


@router.get("/get-languages", dependencies=[Depends(require_htmx)])
async def get_languages(request: Request) -> HTMLResponse:
    """Return a list of supported languages."""
    return render_template(
        "lang/select.html.jinja",
        request=request,
        ctx={"current_language": request.state.language},
    )
