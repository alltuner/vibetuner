# ABOUTME: OAuth provider configuration model (beanie-free).
# ABOUTME: Lives outside models/ to avoid triggering models/__init__.py import chain.
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, ConfigDict


class CapabilityDetector(ABC):
    """Detects capabilities available to an OAuth app from its token response."""

    @abstractmethod
    async def detect(self, token: dict[str, Any]) -> list[str]:
        """Return capability strings detected from the token or provider APIs."""


class ScopeCapabilityDetector(CapabilityDetector):
    """Extracts granted scopes from the OAuth token response."""

    async def detect(self, token: dict[str, Any]) -> list[str]:
        scope = token.get("scope", "")
        if isinstance(scope, list):
            return list(scope)
        if isinstance(scope, str):
            return [s for s in scope.split() if s]
        return []


class OauthProviderModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    identifier: str
    params: dict[str, str] = {}
    scopes: list[str] = []
    client_kwargs: dict[str, str] = {}
    config: dict[str, str] = {}
    compliance_fix: Callable[..., Any] | None = None
    login_routes: bool = True
    capability_detector: CapabilityDetector | None = None
