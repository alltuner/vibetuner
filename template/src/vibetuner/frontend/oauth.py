from typing import Optional

from authlib.integrations.base_client.errors import OAuthError
from authlib.integrations.starlette_client import OAuth  # ty: ignore[unresolved-import]
from fastapi import Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from pydantic_extra_types.language_code import LanguageAlpha2
from starlette.authentication import BaseUser

from vibetuner.frontend.routes import get_homepage_url
from vibetuner.models.oauth import OAuthAccountModel, OauthProviderModel
from vibetuner.models.user import UserModel


DEFAULT_AVATAR_IMAGE = "/statics/img/user-avatar.png"

_PROVIDERS: dict[str, OauthProviderModel] = {}


def register_oauth_provider(name: str, provider: OauthProviderModel) -> None:
    _PROVIDERS[name] = provider
    PROVIDER_IDENTIFIERS[name] = provider.identifier
    _oauth_config.update(**provider.config)
    register_kwargs = {"client_kwargs": provider.client_kwargs, **provider.params}
    oauth.register(name, overwrite=True, **register_kwargs)


class WebUser(BaseUser, BaseModel):
    id: str
    name: str
    email: str
    picture: Optional[str] = Field(
        default=DEFAULT_AVATAR_IMAGE,
        description="URL to the user's avatar image",
    )
    language: Optional[LanguageAlpha2] = Field(
        default=None,
        description="Preferred language for the user",
    )

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.name


class Config:
    def __init__(self, **kwargs):
        self._data = kwargs

    def get(self, key, default=None):
        return self._data.get(key, default)

    def update(self, **kwargs):
        self._data.update(kwargs)


_oauth_config = Config()
oauth = OAuth(_oauth_config)

PROVIDER_IDENTIFIERS: dict[str, str] = {}


def get_oauth_providers() -> list[str]:
    return list(_PROVIDERS.keys())


async def _handle_user_account(
    provider: str, identifier: str, email: str, name: str, picture: str
) -> UserModel:
    """Handle user account creation or OAuth linking."""
    # Check if OAuth account already exists
    oauth_account = await OAuthAccountModel.get_by_provider_and_id(
        provider=provider,
        provider_user_id=identifier,
    )

    if oauth_account:
        # OAuth account exists, get linked user account
        account = await UserModel.get_by_email(email)
        if not account:
            raise OAuthError("No account linked to this OAuth account")
        return account

    # OAuth account doesn't exist, check if user exists

    if account := (await UserModel.get_by_email(email)):
        # User exists, link OAuth account
        await _link_oauth_account(account, provider, identifier, email, name, picture)
    else:
        # New user, create account and OAuth link
        account = await _create_new_user_with_oauth(
            provider, identifier, email, name, picture
        )

    return account


async def _link_oauth_account(
    account: UserModel,
    provider: str,
    identifier: str,
    email: str,
    name: str,
    picture: str,
) -> None:
    """Link OAuth account to existing user."""
    oauth_account = OAuthAccountModel(
        provider=provider,
        provider_user_id=identifier,
        email=email,
        name=name,
        picture=picture,
    )
    await oauth_account.insert()
    account.oauth_accounts.append(oauth_account)
    await account.save()


async def _create_new_user_with_oauth(
    provider: str, identifier: str, email: str, name: str, picture: str
) -> UserModel:
    """Create new user account with OAuth linking."""
    # Create user account
    oauth_account = OAuthAccountModel(
        provider=provider,
        provider_user_id=identifier,
        email=email,
        name=name,
        picture=picture,
    )
    await oauth_account.insert()

    account = UserModel(
        email=email,
        name=name,
        picture=picture,
        oauth_accounts=[oauth_account],
    )
    await account.insert()

    return account


def _create_auth_login_handler(provider_name: str):
    async def auth_login(request: Request, next: str | None = None):
        redirect_uri = request.url_for(f"auth_with_{provider_name}")
        request.session["next_url"] = next or get_homepage_url(request)
        client = oauth.create_client(provider_name)
        if not client:
            return RedirectResponse(url=get_homepage_url(request))

        return await client.authorize_redirect(
            request, redirect_uri, hl=request.state.language
        )

    return auth_login


def _create_auth_handler(provider_name: str):
    async def auth_handler(request: Request):
        """Handle OAuth authentication flow."""
        try:
            # Initialize OAuth client
            client = oauth.create_client(provider_name)
            if not client:
                return get_homepage_url(request)

            # Get user info from OAuth provider
            token = await client.authorize_access_token(request)
            userinfo = token.get("userinfo")
            if not userinfo:
                raise OAuthError("No userinfo found in token")

            # Extract user data
            identifier = userinfo.get(PROVIDER_IDENTIFIERS[provider_name])
            email = userinfo.get("email")
            name = userinfo.get("name")
            picture = userinfo.get("picture")

            # Handle user account creation/linking
            account = await _handle_user_account(
                provider_name, identifier, email, name, picture
            )

            # Set session and redirect
            request.session["user"] = account.session_dict
            return request.session.pop("next_url", get_homepage_url(request))
        except OAuthError:
            return get_homepage_url(request)

    return auth_handler
