# ABOUTME: OAuth provider configuration model (beanie-free).
# ABOUTME: Separated from oauth.py to avoid pulling in beanie at config load time.
from pydantic import BaseModel


class OauthProviderModel(BaseModel):
    identifier: str
    params: dict[str, str] = {}
    client_kwargs: dict[str, str]
    config: dict[str, str]
