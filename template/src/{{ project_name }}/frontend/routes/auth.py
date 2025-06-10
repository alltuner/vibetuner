from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from ..oauth import _create_auth_handler, _create_auth_login_handler, oauth_providers
from ..templates import template_render


router = APIRouter()


@router.get("/auth/logout", response_class=RedirectResponse)
async def auth_logout(request: Request):
    request.session.pop("user", None)

    return request.url_for("homepage", lang=request.state.language).path


for provider in oauth_providers:
    router.get(
        f"/auth/{provider}",
        response_class=RedirectResponse,
        name=f"auth_with_{provider}",
    )(_create_auth_handler(provider))

    router.get(
        f"/auth/login/{provider}",
        name=f"login_with_{provider}",
    )(_create_auth_login_handler(provider))


if oauth_providers:

    @router.get("/auth/login")
    async def auth_login(request: Request, next: str | None = None):
        # Returns the list of available OAuth providers for login

        return template_render(
            "auth.html.jinja",
            request=request,
            ctx={
                "providers": oauth_providers,
                "next": next,
            },
        )
