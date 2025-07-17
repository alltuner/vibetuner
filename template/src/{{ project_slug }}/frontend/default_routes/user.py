from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from starlette.authentication import requires

from ...models.core import UserModel
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
