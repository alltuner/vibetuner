# ABOUTME: OAuth provider configuration model (beanie-free).
# ABOUTME: Lives outside models/ to avoid triggering models/__init__.py import chain.
from pydantic import BaseModel


class OauthProviderModel(BaseModel):
    identifier: str
    params: dict[str, str] = {}
    client_kwargs: dict[str, str]
    config: dict[str, str]
