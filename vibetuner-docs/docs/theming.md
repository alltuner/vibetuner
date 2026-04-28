# Per-Tenant Theming

Multi-tenant Vibetuner apps often need per-tenant visual identity — at minimum
the four DaisyUI role colors and their content variants. Vibetuner ships a
small primitive for this: an embedded `TenantTheme` model, an opt-in context
provider, and a Jinja partial that injects the overrides at request time.

The model is simple: `bundle.css` stays tenant-agnostic and cached, and
theming is per-request HTML — no per-tenant CSS rebuilds.

## How it composes

1. **Bundled CSS defines the role variables.** Tailwind 4 + DaisyUI emit
   `--color-primary`, `--color-secondary`, `--color-accent`, `--color-neutral`
   (and their `*-content` foreground variants) into `bundle.css`.
2. **Each request renders a tiny `<style>:root { ... }</style>` block** after
   the `<link rel="stylesheet" href="bundle.css">`, overriding *only* the
   variables the tenant has set.
3. **Cascade does the rest.** DaisyUI scopes its own theme via
   `:where(:root)` (zero specificity), so a plain `:root { ... }` block always
   wins.

## Add a TenantTheme to your tenant model

```python
from beanie import Document
from pydantic import Field
from vibetuner.models import TenantTheme
from vibetuner.models.mixins import TimeStampMixin


class TenantModel(Document, TimeStampMixin):
    name: str
    slug: str
    theme: TenantTheme = Field(default_factory=TenantTheme)
```

`TenantTheme` exposes eight optional `#rrggbb` fields:

| Field | CSS variable |
| --- | --- |
| `primary` | `--color-primary` |
| `secondary` | `--color-secondary` |
| `accent` | `--color-accent` |
| `neutral` | `--color-neutral` |
| `primary_content` | `--color-primary-content` |
| `secondary_content` | `--color-secondary-content` |
| `accent_content` | `--color-accent-content` |
| `neutral_content` | `--color-neutral-content` |

Hex strings are validated to match `^#[0-9a-fA-F]{6}$` — any other format
raises a Pydantic `ValidationError` at the model layer.

### Backwards compatibility

Adding `theme: TenantTheme = Field(default_factory=TenantTheme)` to an existing
tenant document is a no-op for already-persisted records. MongoDB is
schema-on-read, so old documents load with a default-constructed `TenantTheme`
(all `None`s) and `keep_nulls=False` keeps the field out of the database
until a value is set.

## Wire up the context provider

The provider is **opt-in** — Vibetuner does not auto-register one, so apps
that don't multi-tenant pay nothing. Register it once at startup, with a
synchronous tenant getter that already has the tenant in hand:

```python
from starlette.requests import Request
from vibetuner import register_tenant_theme_provider


def _tenant_from_request(request: Request):
    # Whatever upstream middleware / dependency attached.
    return getattr(request.state, "tenant", None)


register_tenant_theme_provider(_tenant_from_request)
```

The getter must be synchronous and cheap — it runs on every render. Do any
DB lookups in middleware (or a dependency) that fires before the route
executes, and stash the resulting object on `request.state`.

If your tenant model uses a different attribute name (e.g. `branding`
instead of `theme`), pass `attribute="branding"` to
`register_tenant_theme_provider`.

The provider is fail-soft: a getter exception, missing attribute, or wrong
type is logged and the request renders with no overrides rather than 500ing.

## Template integration

Vibetuner's `base/skeleton.html.jinja` already includes
`base/theme.html.jinja` between the bundled stylesheet link and
`{% block head %}`. The partial emits a CSP-noncified
`<style>:root { ... }</style>` only when `theme_overrides` is non-empty, so
apps that haven't registered the provider see no extra markup.

If you've replaced the skeleton wholesale in your project, mirror the same
include order:

```jinja
<link rel="stylesheet" href="{{ url_for('css', path='bundle.css').path }}" />
{% include "base/theme.html.jinja" %}
{% block head %}{% endblock head %}
```

## Footguns

**1. Build-time literals in custom tokens.** A custom `--shadow-glow-primary`
that bakes an rgba literal will never follow theming, because the rgba is a
constant — not a `var(...)` reference:

```css
/* Won't follow the theme */
--shadow-glow-primary: 0 0 80px rgba(0, 157, 220, 0.2);

/* Follows the theme */
--shadow-glow-primary: 0 0 80px color-mix(
  in oklab, var(--color-primary) 20%, transparent
);
```

When you derive a custom token from a role color, always express it in terms
of the role variable.

**2. Hardcoded scale colors mixed into role-driven utilities.** A class like
`bg-linear-to-br from-accent/70 to-tiger-flame-700` mixes one role color with
a fixed-palette shade — only half of it follows the theme. Either keep the
gradient role-only (`from-accent/70 to-accent/30`) or accept that the scale
shade is a brand constant.

**3. Inline `<style>` without a CSP nonce.** The shipped partial sets
`nonce="{{ csp_nonce }}"` automatically; if you write a custom override
template, do the same.

## What this primitive does *not* cover

- **Fonts.** Per-tenant font swapping is genuinely different from color
  injection — `@font-face` rules have to load the binary first, before any
  `--font-display` variable can switch to it. That's tracked separately in
  [vibetuner#1705](https://github.com/alltuner/vibetuner/issues/1705).
- **Logos / favicons / assets.** These are app-specific and don't belong in a
  cross-cutting framework primitive. Wire them through your existing context.
