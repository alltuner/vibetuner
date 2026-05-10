---
paths:
  - templates/frontend/**
  - assets/**
  - src/*/frontend/**
description: HTMX patterns, SSE, caching, block rendering, and Tailwind/DaisyUI
---

# Frontend Patterns

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

**`hx-on` attributes** — the `hx-on::` shorthand is broken in
alpha8. Use the explicit long form:

```html
<!-- BROKEN: hx-on::after-request="..." -->
<!-- WORKS: -->
<form hx-on:htmx:after:request="this.reset()">
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
