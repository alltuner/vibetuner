---
paths:
  - templates/frontend/**
  - assets/**
  - src/*/frontend/**
  - config.css
description: HTMX patterns, SSE, caching, block rendering, and Tailwind/DaisyUI
---

# Frontend Patterns

## DaisyUI palette overrides

To recolor the DaisyUI `light` / `dark` themes for the whole bundle,
override the `[data-theme="…"]` selectors in `config.css` below the
`@import "@alltuner/vibetuner/core.css"`:

```css
[data-theme="light"] {
  --color-primary: oklch(64% 0.21 24);
  --color-primary-content: oklch(98% 0 0);
}
[data-theme="dark"] {
  --color-primary: oklch(64% 0.21 24);
  --color-primary-content: oklch(98% 0 0);
}
```

`core.css` invokes `@plugin "daisyui"`, which emits a rule of the form
`:where(:root),:root:has(input.theme-controller[value=light]:checked),[data-theme=light] { … }`.
The override above shares specificity with the standalone
`[data-theme=light]` matcher and lands later in `config.css` — cascade
picks it up. No `daisyui` install on the consumer side is required.

**Do not write `@plugin "daisyui/theme" { … }` in `config.css`.**
`daisyui` is a private transitive of `@alltuner/vibetuner`; bun's
isolated linker keeps it scoped to that package, so module resolution
from the project root fails with `Error: Can't resolve 'daisyui/theme'`.
Use the `[data-theme="…"]` cascade override above. If a project
genuinely needs a brand-new named theme, add `daisyui` as a direct
devDependency (`bun add -d daisyui`) — but for recoloring the existing
themes, the cascade override is the right tool.

For per-request runtime overrides (per-tenant branding), use
`register_tenant_theme_provider` — see the
[theming guide](https://vibetuner.alltuner.com/theming/).

## SSE

**Import from `vibetuner.sse`** (NOT `vibetuner.frontend.sse`):

```python
from vibetuner.sse import sse_endpoint, broadcast

@sse_endpoint(
    "/events/notifications",
    channel="notifications",
    router=router,
)
async def notifications_stream(request: Request): pass

# Dynamic: return channel name from function body
# Broadcast: await broadcast("channel", "event",
#   data="<html>" or template=..., ctx=...)
# HTMX: <div sse-connect="/events/..." sse-swap="event-name">
```

## HTMX Response Headers

From `vibetuner.htmx`: `hx_redirect(url)`,
`hx_location(path, target=, swap=)`,
`hx_trigger(response, event, detail)`, `hx_push_url`,
`hx_replace_url`, `hx_reswap`, `hx_retarget`, `hx_refresh`,
`hx_trigger_after_settle`, `hx_trigger_after_swap`.

## HTMX 4 Event Handling

htmx 4 changed event handling significantly. Key differences:

**Event names** use colon-separated format (not camelCase):
`htmx:after:request`, `htmx:before:swap`, `htmx:after:settle`.

**`hx-on` attributes** — the `hx-on::` shorthand works in beta1+
(it was broken in alpha8). Both forms are valid:

```html
<form hx-on:htmx:after:request="this.reset()">
<form hx-on::after-request="this.reset()">
```

**`event.detail`** was restructured. `event.detail.successful` no
longer exists. Use `event.detail.ctx.response` instead:

```javascript
// v2: event.detail.successful, event.detail.elt, event.detail.xhr
// v4: event.detail.ctx.response, event.detail.ctx.sourceElement,
//     event.detail.ctx.status
```

**Events do not bubble** to `document.body` in v4. Attach listeners
directly to elements or use `hx-on` attributes.

See the [HTMX migration guide](https://vibetuner.alltuner.com/htmx-migration/)
for full details.

## htmx Nonce Protection (opt-in)

The `hx-nonce` extension (htmx 4.0.0-beta3+) gates htmx attribute
processing behind the page CSP nonce. Framework templates already
stamp `hx-nonce="{{ csp_nonce }}"` on htmx-bearing elements; mirror
that pattern in your own templates if you enable the extension.
Add `import "./node_modules/htmx.org/dist/ext/hx-nonce.js";` to your
`config.js` custom imports section. Elements without a matching
`hx-nonce` will be stripped (fail-closed). See the
[CSP/htmx docs](https://vibetuner.alltuner.com/development-guide/#htmx-nonce-protection-opt-in).

## htmx Live Reactivity (default-on)

`hx-live` is loaded by default from the framework-managed block of
`config.js`. **Use it before reaching for Alpine.js or Stimulus** —
it covers the same client-side-reactivity ground (chip lists, derived
fields, live filters, paired controls, inline validation) without
adding a separate library or breaking the project's "no JavaScript
frameworks" stance.

Quick patterns:

```jinja
{# Derived field that recomputes on every DOM mutation #}
<input type="hidden" name="scopes"
       hx-live="this.value = q('#scopes-tags .badge').arr()
                             .map(b => b.dataset.scope).join(',')">

{# Conditional class from a sibling input #}
<p hx-live="this.classList.toggle('text-error',
                                  q('#age').valueAsNumber < 18)">
  Adult content
</p>

{# Debounced live search (per-element debounce cancels prior calls) #}
<output hx-live="
  let term = q('#q').value;
  if (!term) { this.textContent = ''; return; }
  await debounce(250);
  this.textContent = await fetch('/search?q=' +
    encodeURIComponent(term)).then(r => r.text());
"></output>
```

CSP-safe by design — `hx-on:` / `hx-live` attributes evaluate
through htmx's nonced TrustedTypes path, where raw inline
`onclick="..."` would be blocked by the project's `script-src`
policy.

Gotchas to remember: the DOM is the only source of truth (no
JS-variable reactivity, share state via `data-*` or hidden inputs);
expressions re-run on **any** mutation so guard expensive work with
`debounce`; set-property writes (`q('.x').value = ''`) broadcast to
every match; `q().insert()` is raw `insertAdjacentHTML` and does
not run `htmx.process()` — use event delegation on a stable parent
for handlers on dynamically-inserted elements. Full reference:
<https://four.htmx.org/extensions/hx-live/>.

## Response Caching (Server-Side)

`from vibetuner.cache import cache, invalidate, invalidate_pattern`.
`@cache(expire=60)` — Redis-backed, key from path+query params.
`vary_on=lambda r: str(r.state.user.id)` for per-user/tenant keys.
Disabled in debug mode (`force_caching=True` to override).
No-op without Redis.

## Cache Control (Browser-Side)

`from vibetuner.decorators import cache_control`.
`@cache_control(max_age=300, public=True)`. Supports: `public`,
`private`, `no_cache`, `no_store`, `max_age`, `s_maxage`,
`must_revalidate`, `stale_while_revalidate`, `immutable`.

## Block Rendering for HTMX Partials

`render_template_block("template.html.jinja", "block_name",
request, ctx)` — renders a single `{% block %}`.
`render_template_blocks(...)` (plural) for multi-block OOB swaps.

## HTMX Request Detection

`request.state.htmx` — truthy for HTMX requests. Properties:
`.boosted`, `.target`, `.trigger`, `.trigger_name`, `.current_url`,
`.prompt`. Use `Depends(require_htmx)` for HTMX-only routes.
