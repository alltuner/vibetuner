from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Form,
    HTTPException,
    Request,
)
from fastapi.responses import RedirectResponse
from pydantic import EmailStr
from starlette.responses import HTMLResponse

from vibetuner.models import EmailVerificationTokenModel, UserModel
from vibetuner.services.email import SESEmailService

from ..email import send_magic_link_email
from ..oauth import (
    _create_auth_handler,
    _create_auth_login_handler,
    get_oauth_providers,
)
from ..templates import render_template
from . import get_homepage_url


def get_ses_service() -> SESEmailService:
    return SESEmailService()


def logout_user(request: Request):
    request.session.pop("user", None)


router = APIRouter(prefix="/auth")


@router.get(
    "/logout",
    dependencies=[Depends(logout_user)],
    response_class=RedirectResponse,
    status_code=307,
)
async def auth_logout(request: Request):
    return get_homepage_url(request)


@router.get("/login", response_model=None)
async def auth_login(
    request: Request,
    next: str | None = None,
) -> RedirectResponse | HTMLResponse:
    """Display unified login page with all available options"""
    if request.user.is_authenticated:
        # If user is already authenticated, redirect to homepage
        return RedirectResponse(url=get_homepage_url(request), status_code=302)

    oauth_providers = get_oauth_providers()
    return render_template(
        "login.html.jinja",
        request=request,
        ctx={
            "providers": oauth_providers,
            "next": next,
            "has_oauth": bool(oauth_providers),
            "has_email": True,
        },
    )


@router.post("/magic-link-login", response_model=None)
async def send_magic_link(
    request: Request,
    ses_service: Annotated[SESEmailService, Depends(get_ses_service)],
    background_tasks: BackgroundTasks,
    email: Annotated[EmailStr, Form()],
    next: Annotated[str | None, Form()] = None,
) -> HTMLResponse:
    """Handle email magic link login form submission"""

    # Create verification token
    verification_token = await EmailVerificationTokenModel.create_token(email)

    # Build login URL
    login_url = request.url_for("email_verify", token=verification_token.token)
    if next:
        login_url = login_url.include_query_params(next=next)

    background_tasks.add_task(
        send_magic_link_email,
        ses_service=ses_service,
        lang=request.state.language,
        to_address=email,
        login_url=str(login_url),
    )

    return render_template(
        "email_sent.html.jinja", request=request, ctx={"email": email, "next": next}
    )


@router.get(
    "/email-verify/{token}",
    response_class=RedirectResponse,
    status_code=302,
    response_model=None,
)
async def email_verify(
    request: Request,
    token: str,
    next: str | None = None,
) -> str:
    """Verify email token and log in user"""
    # Verify token
    verification_token = await EmailVerificationTokenModel.verify_token(token)
    if not verification_token:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    # Get or create user
    user = await UserModel.get_by_email(verification_token.email)
    if not user:
        # Create new user
        user = UserModel(
            email=verification_token.email,
            # Use email prefix as default name
            name=verification_token.email.split("@")[0],
        )
        await user.insert()

    # Set session
    request.session["user"] = user.session_dict

    # Redirect
    return next or get_homepage_url(request)


def register_oauth_routes() -> None:
    """Register OAuth provider routes dynamically.

    This must be called after OAuth providers are registered to ensure
    routes are created for all configured providers.
    """
    for provider in get_oauth_providers():
        router.get(
            f"/provider/{provider}",
            response_class=RedirectResponse,
            name=f"auth_with_{provider}",
            response_model=None,
        )(_create_auth_handler(provider))

        router.get(
            f"/login/provider/{provider}",
            name=f"login_with_{provider}",
            response_model=None,
        )(_create_auth_login_handler(provider))
