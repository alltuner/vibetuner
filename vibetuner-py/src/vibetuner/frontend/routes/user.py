from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic_extra_types.language_code import LanguageAlpha2
from starlette.authentication import requires

from vibetuner.models import UserModel

from ..context import ctx
from ..templates import render_template


router = APIRouter(prefix="/user")


@router.get("/")
@requires("authenticated", redirect="auth_login")
async def user_profile(request: Request) -> HTMLResponse:
    """User profile endpoint."""
    user = await UserModel.get(request.user.id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    await user.fetch_link("oauth_accounts")
    return render_template(
        "user/profile.html.jinja",
        request,
        {"user": user},
    )


@router.get("/edit")
@requires("authenticated", redirect="auth_login")
async def user_edit_form(request: Request) -> HTMLResponse:
    """User profile edit form."""
    user = await UserModel.get(request.user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get available languages for the dropdown
    from babel import Locale

    locale_names = dict(
        sorted(
            {
                locale: (Locale.parse(locale).display_name or locale).capitalize()
                for locale in ctx.supported_languages
            }.items(),
            key=lambda x: x[1],
        ),
    )

    return render_template(
        "user/edit.html.jinja",
        request,
        {
            "user": user,
            "locale_names": locale_names,
            "current_language": user.user_settings.language,
        },
    )


@router.post("/edit")
@requires("authenticated", redirect="auth_login")
async def user_edit_submit(
    request: Request,
    name: str = Form(...),
    language: str = Form(None),
) -> RedirectResponse:
    """Handle user profile edit form submission."""
    user = await UserModel.get(request.user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update user fields
    user.name = name

    # Update language preference if provided
    if language and language in ctx.supported_languages:
        try:
            user.user_settings.language = LanguageAlpha2(language)
        except ValueError:
            pass  # Invalid language code, skip update

    # Save user
    await user.save()

    # Update session with new data to avoid DB query on next request
    request.session["user"] = user.session_dict

    return RedirectResponse(url="/user/", status_code=302)
