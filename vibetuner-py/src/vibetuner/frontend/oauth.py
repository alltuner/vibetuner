# ABOUTME: OAuth provider integration using Authlib.
# ABOUTME: Handles provider registration, builtin configs, and auth flow handlers.
from typing import Optional

from authlib.integrations.base_client.errors import OAuthError
from authlib.integrations.starlette_client import OAuth
from fastapi import Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from pydantic_extra_types.language_code import LanguageAlpha2
from starlette.authentication import BaseUser

from vibetuner.frontend.routes import get_homepage_url
from vibetuner.logging import logger
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


_BUILTIN_PROVIDERS: dict[str, OauthProviderModel] = {
    "google": OauthProviderModel(
        identifier="sub",
        params={
            "server_metadata_url": "https://accounts.google.com/.well-known/openid-configuration",
        },
        client_kwargs={"scope": "openid email profile"},
        config={},
    ),
    "github": OauthProviderModel(
        identifier="id",
        params={
            "authorize_url": "https://github.com/login/oauth/authorize",
            "access_token_url": "https://github.com/login/oauth/access_token",
            "api_base_url": "https://api.github.com/",
            "userinfo_endpoint": "https://api.github.com/user",
        },
        client_kwargs={"scope": "user:email"},
        config={},
    ),
}


def auto_register_providers(
    provider_names: list[str],
    custom_providers: dict[str, OauthProviderModel] | None = None,
) -> None:
    """Register OAuth providers from builtin configs, settings credentials, and custom configs."""
    from vibetuner.config import settings

    known = sorted(_BUILTIN_PROVIDERS.keys())
    for name in provider_names:
        if name not in _BUILTIN_PROVIDERS:
            logger.warning(f"Unknown OAuth provider '{name}', known providers: {known}")
            continue

        client_id = getattr(settings, f"{name}_client_id", None)
        client_secret = getattr(settings, f"{name}_client_secret", None)

        if not client_id or not client_secret:
            logger.warning(
                f"Skipping OAuth provider '{name}': "
                f"set {name}_client_id and {name}_client_secret in env or .env"
            )
            continue

        env_prefix = name.upper()
        builtin = _BUILTIN_PROVIDERS[name]
        provider = OauthProviderModel(
            identifier=builtin.identifier,
            params=builtin.params,
            client_kwargs=builtin.client_kwargs,
            config={
                **builtin.config,
                f"{env_prefix}_CLIENT_ID": client_id.get_secret_value(),
                f"{env_prefix}_CLIENT_SECRET": client_secret.get_secret_value(),
            },
        )
        register_oauth_provider(name, provider)
        logger.info(f"Auto-registered OAuth provider: {name}")

    # Register custom providers (fully configured by the user)
    for name, provider in (custom_providers or {}).items():
        if not isinstance(name, str):
            logger.warning(
                f"Skipping custom OAuth provider with non-string key: {name!r}"
            )
            continue
        if not isinstance(provider, OauthProviderModel):
            logger.warning(
                f"Skipping custom OAuth provider '{name}': expected OauthProviderModel, "
                f"got {type(provider).__name__}"
            )
            continue
        if name in _PROVIDERS:
            logger.warning(
                f"Custom OAuth provider '{name}' conflicts with already-registered provider, skipping"
            )
            continue
        register_oauth_provider(name, provider)
        logger.info(f"Registered custom OAuth provider: {name}")


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
        # OAuth account exists, resolve user through the link (survives email changes)
        account = await UserModel.find_one({"oauth_accounts.$id": oauth_account.id})
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


def _get_relay_cookie_domain(relay_url: str) -> str:
    """Extract parent domain from relay URL for cookie sharing.

    "https://oauth.localdev.alltuner.com:28000" -> ".localdev.alltuner.com"
    """
    from urllib.parse import urlparse

    host = urlparse(relay_url).hostname or ""
    # Strip the first label (e.g. "oauth") to get parent domain
    parts = host.split(".", 1)
    return f".{parts[1]}" if len(parts) > 1 else host


def _get_source_port(request: Request) -> str:
    """Extract the app port from the request host.

    "8001.localdev.alltuner.com:28000" -> "8001"
    """
    host = request.url.hostname or ""
    return host.split(".")[0]


def _create_auth_login_handler(provider_name: str):
    async def auth_login(request: Request, next: str | None = None):
        from vibetuner.config import settings

        request.session["next_url"] = next or get_homepage_url(request)
        client = oauth.create_client(provider_name)
        if not client:
            return RedirectResponse(url=get_homepage_url(request))

        if settings.oauth_relay_url and settings.environment == "dev":
            relay_url = settings.oauth_relay_url.rstrip("/")
            redirect_uri = f"{relay_url}/auth/provider/{provider_name}"
            response = await client.authorize_redirect(
                request, redirect_uri, hl=request.state.language
            )
            domain = _get_relay_cookie_domain(relay_url)
            port = _get_source_port(request)
            response.set_cookie(
                "_oauth_source_port",
                port,
                max_age=300,
                httponly=True,
                secure=True,
                domain=domain,
                path="/auth/provider/",
            )
            return response

        redirect_uri = request.url_for(f"auth_with_{provider_name}")
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
