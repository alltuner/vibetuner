# ABOUTME: Opt-in helper that wires a tenant getter into the template context
# ABOUTME: as ``theme_overrides`` for the shipped base/theme.html.jinja partial.
"""Per-tenant theming via runtime CSS-variable injection.

This module ships the opt-in glue that connects an app's tenant lookup to the
:class:`vibetuner.models.TenantTheme` model and the shipped
``base/theme.html.jinja`` partial. Apps register a synchronous tenant *getter*
once at startup; on every render, the getter pulls the tenant off the request,
and ``.theme.overrides()`` is exposed as ``theme_overrides`` in the template
context.

The getter is intentionally synchronous — context providers run on every render
and must not perform DB I/O. The tenant is expected to already be attached to
``request.state`` (or accessible from another sync source) by middleware /
dependency code that ran upstream.

Example::

    from vibetuner.theming import register_tenant_theme_provider

    def _tenant_from_request(request):
        return getattr(request.state, "tenant", None)

    register_tenant_theme_provider(_tenant_from_request)

The helper is opt-in: until ``register_tenant_theme_provider`` is called, no
provider is registered and ``base/theme.html.jinja`` renders nothing.
"""

from collections.abc import Callable
from typing import Any, Protocol, runtime_checkable

from starlette.requests import Request

from vibetuner.logging import logger
from vibetuner.models import TenantTheme
from vibetuner.rendering import register_context_provider


__all__ = ["register_tenant_theme_provider"]


@runtime_checkable
class _ThemeBearer(Protocol):
    """Anything exposing a ``.theme`` attribute that yields a TenantTheme."""

    theme: TenantTheme


TenantGetter = Callable[[Request], object | None]


def register_tenant_theme_provider(
    getter: TenantGetter,
    *,
    attribute: str = "theme",
) -> None:
    """Register a context provider that exposes ``theme_overrides``.

    The ``getter`` is called once per render with the current
    :class:`~starlette.requests.Request`. It should return the tenant object
    (or ``None`` if the current request has no tenant, e.g. unauthenticated
    pages or a default landing page). The tenant's
    ``getattr(tenant, attribute)`` is expected to be a :class:`TenantTheme`
    instance whose ``.overrides()`` produces the ``{css_var: hex}`` map.

    The provider is fail-soft: any exception raised by ``getter`` or
    ``.overrides()`` is logged and the request renders with no theme overrides
    rather than 500ing.

    Args:
        getter: Callable that returns the tenant for a given request.
            Must be synchronous; do any DB lookups in upstream middleware.
        attribute: Name of the :class:`TenantTheme` attribute on the tenant
            object. Defaults to ``"theme"``.
    """

    def tenant_theme_context(request: Request) -> dict[str, Any]:
        try:
            tenant = getter(request)
        except Exception as exc:
            logger.error(f"tenant_theme_context: getter raised {exc!r}")
            return {}
        if tenant is None:
            return {}
        theme = getattr(tenant, attribute, None)
        if theme is None:
            return {}
        if not isinstance(theme, TenantTheme):
            logger.error(
                f"tenant_theme_context: expected TenantTheme on '{attribute}', "
                f"got {type(theme).__name__}"
            )
            return {}
        try:
            overrides = theme.overrides()
        except Exception as exc:
            logger.error(f"tenant_theme_context: .overrides() raised {exc!r}")
            return {}
        if not overrides:
            return {}
        return {"theme_overrides": overrides}

    register_context_provider(tenant_theme_context)
