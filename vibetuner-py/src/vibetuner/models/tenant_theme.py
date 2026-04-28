# ABOUTME: TenantTheme embedded model for per-tenant runtime CSS-variable theming.
# ABOUTME: Apps embed it on their tenant document and call .overrides() to get the {css_var: hex} map.
"""Tenant-scoped color theme overrides for DaisyUI role colors.

Apps that need per-tenant visual identity embed :class:`TenantTheme` on their
tenant document::

    from vibetuner.models import TenantTheme

    class TenantModel(Document, TimeStampMixin):
        name: str
        theme: TenantTheme = Field(default_factory=TenantTheme)

The model holds the eight DaisyUI role / role-content colors as optional
``#rrggbb`` strings. :meth:`TenantTheme.overrides` returns a mapping suitable
for runtime ``:root { ... }`` injection by the shipped ``base/theme.html.jinja``
partial. ``bundle.css`` stays tenant-agnostic and cached; theming happens at
request time in HTML, not via per-tenant CSS rebuilds.
"""

import re
from typing import ClassVar

from pydantic import BaseModel, Field, field_validator


_HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


class TenantTheme(BaseModel):
    """Per-tenant overrides for DaisyUI role colors.

    All fields are optional. Unset fields are omitted from
    :meth:`overrides`, so the shipped CSS values from ``bundle.css`` continue
    to apply.

    Field-to-CSS-variable mapping:

    ============== =========================
    Field          CSS variable
    ============== =========================
    primary        ``--color-primary``
    secondary      ``--color-secondary``
    accent         ``--color-accent``
    neutral        ``--color-neutral``
    primary_content   ``--color-primary-content``
    secondary_content ``--color-secondary-content``
    accent_content    ``--color-accent-content``
    neutral_content   ``--color-neutral-content``
    ============== =========================
    """

    primary: str | None = Field(
        default=None,
        description="DaisyUI primary role color (#rrggbb).",
    )
    secondary: str | None = Field(
        default=None,
        description="DaisyUI secondary role color (#rrggbb).",
    )
    accent: str | None = Field(
        default=None,
        description="DaisyUI accent role color (#rrggbb).",
    )
    neutral: str | None = Field(
        default=None,
        description="DaisyUI neutral role color (#rrggbb).",
    )
    primary_content: str | None = Field(
        default=None,
        description="Foreground color used on top of `primary` (#rrggbb).",
    )
    secondary_content: str | None = Field(
        default=None,
        description="Foreground color used on top of `secondary` (#rrggbb).",
    )
    accent_content: str | None = Field(
        default=None,
        description="Foreground color used on top of `accent` (#rrggbb).",
    )
    neutral_content: str | None = Field(
        default=None,
        description="Foreground color used on top of `neutral` (#rrggbb).",
    )

    _CSS_VAR_BY_FIELD: ClassVar[dict[str, str]] = {
        "primary": "--color-primary",
        "secondary": "--color-secondary",
        "accent": "--color-accent",
        "neutral": "--color-neutral",
        "primary_content": "--color-primary-content",
        "secondary_content": "--color-secondary-content",
        "accent_content": "--color-accent-content",
        "neutral_content": "--color-neutral-content",
    }

    @field_validator(
        "primary",
        "secondary",
        "accent",
        "neutral",
        "primary_content",
        "secondary_content",
        "accent_content",
        "neutral_content",
        mode="before",
    )
    @classmethod
    def _validate_hex(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str) or not _HEX_COLOR_RE.match(value):
            raise ValueError(
                f"Theme color must be a 7-character #rrggbb hex string, got {value!r}"
            )
        return value.lower()

    def overrides(self) -> dict[str, str]:
        """Return the ``{css_var: hex}`` map for set fields.

        Unset fields are omitted, so callers can render an empty ``:root { }``
        block (or skip rendering entirely) when no overrides are configured.
        """
        return {
            self._CSS_VAR_BY_FIELD[field]: value
            for field, value in self.model_dump(exclude_none=True).items()
            if field in self._CSS_VAR_BY_FIELD and value
        }
