# Theming

Vibetuner separates **build-time brand palette** (one set of role colors
baked into `bundle.css`) from **runtime per-tenant overrides** (a small
`<style>` block injected per request). Both pivot on the same cascade
trick — overriding the variables DaisyUI emits, not the plugin that emits
them.

## Build-time brand palette

DaisyUI's `light` and `dark` themes are emitted by `@plugin "daisyui"`
inside `@alltuner/vibetuner/core.css`. To customise the four role colors
across the whole bundle, override the `[data-theme="…"]` selectors
directly in your project's `config.css`:

```css
@import "@alltuner/vibetuner/core.css";
@source "templates";
@source "assets/statics/js";

[data-theme="light"] {
  --color-primary: oklch(64% 0.21 24);
  --color-primary-content: oklch(98% 0 0);
  --color-accent: oklch(82% 0.18 95);
}

[data-theme="dark"] {
  --color-primary: oklch(64% 0.21 24);
  --color-primary-content: oklch(98% 0 0);
  --color-accent: oklch(82% 0.18 95);
}
```

DaisyUI emits a rule like
`:where(:root),:root:has(input.theme-controller[value=light]:checked),[data-theme=light] { … }`.
The override above has the same specificity as the standalone
`[data-theme=light]` matcher and lands later in the file — cascade
picks the consumer rules.

**Caveat — DaisyUI theme-controller radio inputs.** If your UI uses
DaisyUI's `<input class="theme-controller" value="light">` switcher
pattern (without setting `data-theme` on the root element), the
selector that matches at runtime is
`:root:has(input.theme-controller[value=light]:checked)`, which has
higher specificity than `[data-theme="light"]`. The override is then
bypassed for that path. Most projects set `data-theme` on `<html>`
directly, where the override pattern works as expected.

**Escape hatch — brand-new named themes.** DaisyUI's documented
`@plugin "daisyui/theme" { name: "my-brand"; … }` form lets projects
register entirely new themes. It is **not** reachable from a
consumer-side `config.css` by default: `daisyui` is a private
transitive of `@alltuner/vibetuner`, so bun's isolated linker keeps
it out of the project's root `node_modules`. Add it explicitly when
you need this:

```bash
bun add -d daisyui
bun install
```

The top-level symlink makes `@plugin "daisyui/theme"` resolvable from
`config.css`. Most projects don't need this — overriding
`[data-theme="…"]` is enough.

## Per-tenant theming

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

**4. Tailwind v3 raw-RGB tokens in `@theme`.** If you extend your project's
`config.css` with a custom brand palette using the pre-Tailwind-v4
raw-triplet pattern, the tokens look fine for direct utility usage but
collapse the moment they flow through `@apply`:

```css
@theme {
  --color-brand-red: 239 68 68;
}

/* Cascade override that recovers a valid color for direct class usage */
.bg-brand-red { background-color: rgb(var(--color-brand-red)); }
```

`class="bg-brand-red"` resolves correctly because the cascade-override
wins on source order. But Tailwind v4 expands
`@apply bg-brand-red` by inlining its own auto-generated rule for the
token (`background-color: var(--color-brand-red)`), **not** the
override:

```css
@utility btn-brand-primary {
  @apply bg-brand-red text-white;
}

/* Compiles to: */
.btn-brand-primary {
  background-color: var(--color-brand-red);  /* resolves to "239 68 68" — invalid */
  color: var(--color-white);
}
```

`239 68 68` isn't a valid color value, so the property is
invalid-at-computed-value-time and dropped — the element renders fully
transparent. Define `@theme` tokens as full color values instead, and
drop the cascade-override classes (Tailwind v4 auto-generates the
`.bg-*` / `.text-*` utilities from `@theme`):

```css
@theme {
  --color-brand-red: rgb(239 68 68);  /* or oklch(...) / #ef4444 */
}
```

## What this primitive does *not* cover

- **Fonts.** Per-tenant font swapping is genuinely different from color
  injection — `@font-face` rules have to load the binary first, before any
  `--font-display` variable can switch to it. That's tracked separately in
  [vibetuner#1705](https://github.com/alltuner/vibetuner/issues/1705).
- **Logos / favicons / assets.** These are app-specific and don't belong in a
  cross-cutting framework primitive. Wire them through your existing context.
