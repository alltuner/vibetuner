# HTMX v2 to v4 Migration Guide

This guide covers the breaking changes when upgrading from htmx v2 to v4
in Vibetuner projects. It also documents what changed between htmx 4
pre-release versions (alpha → beta1 → beta3), so users on any
pre-release can migrate.

## Quick Start

The two biggest behavioral changes from v2 to v4:

1. **Attribute inheritance is explicit** (was implicit in v2)
2. **Error responses (4xx/5xx) swap by default** (were skipped in v2)

To restore v2 behavior while you migrate incrementally, add this before
loading htmx:

```html
<script>
    htmx.config.implicitInheritance = true;
    htmx.config.noSwap = [204, 304, '4xx', '5xx'];
</script>
```

Or load the `htmx-2-compat` extension, which restores implicit inheritance,
old event names, and previous error-swapping defaults:

```javascript
import "htmx.org/dist/ext/htmx-2-compat.js";
```

## Error Response Swapping

htmx 4 swaps all HTTP responses by default. Only `204` and `304` are skipped.

In v2, `4xx` and `5xx` responses were not swapped. In v4, if your server
returns HTML with a `422` or `500`, that HTML gets swapped into the target.
This means your error responses need to produce valid swap content.

**Options:**

- Design error responses as HTML fragments suitable for swapping
- Use the new [`hx-status`](#per-status-code-swap-control) attribute for
  fine-grained control
- Revert globally: `htmx.config.noSwap = [204, 304, '4xx', '5xx']`

## Per-Status-Code Swap Control

The new `hx-status` attribute lets you control swap behavior per HTTP
status code:

```html
<form hx-post="/save"
      hx-status:422="swap:innerHTML target:#errors select:#validation-errors"
      hx-status:5xx="swap:none push:false">
    <!-- form fields -->
</form>
```

Available config keys: `swap:`, `target:`, `select:`, `push:`, `replace:`,
`transition:`.

Supports exact codes (`404`), single-digit wildcards (`50x`), and range
wildcards (`5xx`). Evaluated in order of specificity.

## Attribute Inheritance Requires `:inherited`

In v2, many htmx attributes were inherited by child elements automatically. In v4,
inheritance must be explicitly opted into using the `:inherited` modifier.

**Before (v2):**

```html
<div hx-target="#results">
    <!-- All children inherit hx-target="#results" -->
    <button hx-get="/search">Search</button>
    <button hx-get="/filter">Filter</button>
</div>
```

**After (v4):**

```html
<div hx-target:inherited="#results">
    <!-- Children inherit hx-target via :inherited modifier -->
    <button hx-get="/search">Search</button>
    <button hx-get="/filter">Filter</button>
</div>
```

Without `:inherited`, each child element must set its own attributes explicitly.

Use `:append` to add to an inherited value instead of replacing it:

```html
<div hx-include:inherited="#global-fields">
    <form hx-include:inherited:append=".extra">...</form>
</div>
```

## Multi-Target Updates with `<hx-partial>`

`<hx-partial>` is a new alternative to `hx-swap-oob` for targeting multiple
elements from one response:

```html
<hx-partial hx-target="#messages" hx-swap="beforeend">
    <div>New message</div>
</hx-partial>
<hx-partial hx-target="#count">
    <span>5</span>
</hx-partial>
```

Each `<hx-partial>` specifies its own `hx-target` and `hx-swap` strategy.

!!! note
    OOB swap order changed in v4: the main content swaps first, then
    OOB and `<hx-partial>` elements swap after (in document order). In v2,
    OOB elements swapped before the main content.

## SSE: Native Support Replaces Extension

htmx v4 includes Server-Sent Events support in core. The separate `sse` extension
and `hx-ext="sse"` attribute are no longer needed.

**Before (v2):**

```html
<div hx-ext="sse" sse-connect="/events/notifications" sse-swap="update">
    <!-- updates appear here -->
</div>
```

**After (v4):**

```html
<div sse-connect="/events/notifications" sse-swap="update">
    <!-- updates appear here -->
</div>
```

The `sse-connect` and `sse-swap` attributes work exactly the same, just remove
`hx-ext="sse"` from the element.

!!! warning
    The SSE and WebSocket extensions were significantly rewritten for v4.
    If you use advanced SSE/WS features (custom config, event handling),
    see the upstream upgrade guides:
    [SSE](https://four.htmx.org/docs/extensions/sse#upgrading-from-htmx-2x),
    [WS](https://four.htmx.org/docs/extensions/ws#upgrading-from-htmx-2x).

## Extension Auto-Registration

In v2, extensions had to be explicitly activated via `hx-ext="..."` on each element
or a parent. In v4, extensions auto-register when imported, no `hx-ext` attribute
needed.

**Before (v2):**

```html
<body hx-ext="preload">
    <a hx-get="/page" preload="mouseover">Link</a>
</body>
```

**After (v4):**

```html
<body>
    <a hx-get="/page" preload="mouseover">Link</a>
</body>
```

Extensions activate automatically once their script is loaded.

To restrict which extensions can register, use an allow list:

```html
<meta name="htmx-config" content='{"extensions": "preload, sse"}'>
```

## `hx-vars` Replaced by `hx-vals` with `js:` Prefix

The `hx-vars` attribute (which evaluated JavaScript expressions) has been removed.
Use `hx-vals` with the `js:` prefix instead.

**Before (v2):**

```html
<button hx-post="/api/action"
        hx-vars="csrfToken:getCsrfToken(), timestamp:Date.now()">
    Submit
</button>
```

**After (v4):**

```html
<button hx-post="/api/action"
        hx-vals='js:{"csrfToken": getCsrfToken(), "timestamp": Date.now()}'>
    Submit
</button>
```

!!! note
    Plain `hx-vals` (without `js:` prefix) still works for static JSON values and
    is unchanged.

## `hx-disable` Renamed to `hx-ignore`

The attribute that prevents htmx from processing an element has been renamed.
Do this rename **before** upgrading, because `hx-disable` means something
different in v4 (it now does what `hx-disabled-elt` used to do).

Rename in this order to avoid conflicts:

1. Rename `hx-disable` to `hx-ignore`
2. Rename `hx-disabled-elt` to `hx-disable`

## JavaScript Import Changes

htmx v4 uses a default export. The import pattern in your `config.js` (or equivalent
entry point) must be updated.

**Before (v2):**

```javascript
import "htmx.org";
```

**After (v4):**

```javascript
import htmx from "@alltuner/vibetuner/htmx";
window.htmx = htmx;
```

The default import is required, and you must explicitly assign `htmx` to `window` for
it to be available globally (e.g., in inline scripts or the browser console).

`@alltuner/vibetuner` re-exports htmx as a subpath, so scaffolded projects don't need
`htmx.org` as a direct dependency. The bare-specifier import works under any package
manager linker mode (Bun hoisted or isolated, pnpm-style stores, npm v9+ isolated).

### Preload Extension

The preload extension moved from a separate package to a built-in module.

**Before (v2):**

```javascript
import "htmx-ext-preload";
```

**After (v4):**

```javascript
import "@alltuner/vibetuner/htmx/preload";
```

### SSE Extension

The SSE extension also moved from a separate package to a built-in module.

**Before (v2):**

```javascript
import "htmx-ext-sse";
```

**After (v4):**

```javascript
import "@alltuner/vibetuner/htmx/sse";
```

Use `hx-sse:connect="/events"` (and `hx-sse:swap`, `hx-sse:close`) on elements
that should subscribe to a server-sent events stream. The `hx-ext="sse"`
attribute is no longer needed — the extension auto-registers on import.

## Event Names Changed from camelCase to Colon-Separated

All htmx event names switched from camelCase to a colon-separated
`htmx:phase:action` format.

**Before (v2):**

```javascript
document.addEventListener("htmx:afterRequest", handler);
document.addEventListener("htmx:beforeSwap", handler);
document.addEventListener("htmx:afterSettle", handler);
```

**After (v4):**

```javascript
element.addEventListener("htmx:after:request", handler);
element.addEventListener("htmx:before:swap", handler);
element.addEventListener("htmx:after:swap", handler);
```

Key renames:

| htmx 2.x | htmx 4.x |
|---|---|
| `htmx:afterOnLoad` | `htmx:after:init` |
| `htmx:afterProcessNode` | `htmx:after:init` |
| `htmx:afterRequest` | `htmx:after:request` |
| `htmx:afterSettle` | `htmx:after:swap` |
| `htmx:afterSwap` | `htmx:after:swap` |
| `htmx:beforeRequest` | `htmx:before:request` |
| `htmx:beforeSwap` | `htmx:before:swap` |
| `htmx:configRequest` | `htmx:config:request` |
| `htmx:responseError` | `htmx:response:error` (added in beta3) |

All error events are consolidated to `htmx:error`. As of beta3, the
specific `htmx:response:error` event also fires for 4xx/5xx responses,
restoring the convenience of htmx 2's `htmx:responseError` for handlers
that only care about HTTP error status codes.

!!! warning
    Events no longer bubble to `document.body` in v4. You must attach listeners
    directly to the element or use `hx-on` attributes. Delegation patterns like
    `document.body.addEventListener('htmx:after:request', ...)` do not work.

## Event Handler Attributes (`hx-on`)

The `hx-on::` shorthand uses kebab-case event names (DOM attributes are
case-insensitive):

```html
<!-- These are equivalent -->
<button hx-get="/info" hx-on:htmx:before-request="alert('Request!')">
<button hx-get="/info" hx-on::before-request="alert('Request!')">
```

!!! note
    The `hx-on::` shorthand was broken in alpha8 but is fixed in beta1.
    If you are upgrading from alpha8, you can now use the shorter form.

For JSX compatibility, dashes can replace colons:

```html
<button hx-get="/info" hx-on--before-request="alert('Request!')">
```

## Event Detail Structure Changed

The `event.detail` object was restructured. Properties that existed at the top level
are now nested under `event.detail.ctx`.

**Before (v2):**

```javascript
event.detail.successful   // boolean
event.detail.elt          // the triggering element
event.detail.xhr          // XMLHttpRequest object
```

**After (v4):**

```javascript
event.detail.ctx                // context object
event.detail.ctx.sourceElement  // the triggering element
event.detail.ctx.response       // response object
event.detail.ctx.status         // request status string
```

!!! danger
    `event.detail.successful` is `undefined` in v4, which is falsy. Any code
    checking `if(event.detail.successful)` silently skips the handler body
    without errors.

## `fetch()` Replaces `XMLHttpRequest`

All requests use the native `fetch()` API. This cannot be reverted. If you
have code that interacts with `XMLHttpRequest` objects (e.g., via
`event.detail.xhr`), it must be updated to use the `Response` object
available at `event.detail.ctx.response`.

## `hx-delete` Excludes Form Data

Like `hx-get`, `hx-delete` no longer includes the enclosing form's inputs.
Add `hx-include="closest form"` where needed.

## `hx-swap` Scroll Modifier Syntax Changed

The `show` and `scroll` modifiers no longer support the combined
`selector:position` syntax. Use separate keys:

```html
<!-- v2 (broken in v4) -->
<div hx-swap="innerHTML show:#other:top"></div>

<!-- v4 -->
<div hx-swap="innerHTML show:top showTarget:#other"></div>
<div hx-swap="innerHTML scroll:bottom scrollTarget:#other"></div>
```

## Config Key Renames

Several config keys were renamed:

| htmx 2.x | htmx 4.x |
|---|---|
| `globalViewTransitions` | `transitions` |
| `defaultSwapStyle` | `defaultSwap` |
| `historyEnabled` | `history` |
| `includeIndicatorStyles` | `includeIndicatorCSS` |
| `timeout` | `defaultTimeout` |

As of beta3, **`htmx.config.prefix`** defaults to `"data-hx-"`, so
both `hx-*` and `data-hx-*` attributes work out of the box (matching
htmx 2 behavior). Set to `""` to disable the data-prefixed alias.
Vibetuner templates use the canonical `hx-*` form; no change needed.

Changed defaults:

| Config | htmx 2 | htmx 4 |
|---|---|---|
| `defaultTimeout` | `0` (no timeout) | `60000` (60 seconds) |
| `defaultSettleDelay` | `20` | `1` |

!!! warning
    The 60-second default timeout may break long-running requests. If you
    have endpoints that take longer, set `htmx.config.defaultTimeout = 0`
    or increase the value.

## View Transitions

View transitions are disabled by default in htmx 4 beta1 (`transitions: false`).

Earlier alpha releases (alpha2 through alpha8) had view transitions enabled
by default, which caused ~500ms UI blocking after each request
([htmx#3566](https://github.com/bigskysoftware/htmx/issues/3566)).
Vibetuner previously included a `<meta>` tag to disable them as a
workaround. That tag has been removed since beta1 defaults to disabled.

If you had added `{"globalViewTransitions": false}` to your own templates
as a workaround, you can safely remove it. The old config key name is
ignored in beta1.

To enable view transitions, set `htmx.config.transitions = true` and add
CSS transition rules per the
[htmx view transitions docs](https://four.htmx.org/reference/config/htmx-config-transitions).

## Removed Attributes

| Removed | Use instead |
|---|---|
| `hx-vars` | `hx-vals` with `js:` prefix |
| `hx-params` | `htmx:config:request` event |
| `hx-prompt` | `hx-confirm` with `js:` prefix |
| `hx-ext` | Include extension script directly |
| `hx-disinherit` | Not needed (inheritance is explicit) |
| `hx-inherit` | Not needed (inheritance is explicit) |
| `hx-request` | `hx-config` |
| `hx-history` | Removed (no localStorage in v4) |

!!! note
    `hx-history-elt` was removed in earlier 4.x pre-releases but
    **restored in beta3** alongside an improved `hx-history-cache`
    extension. Use it as you did in htmx 2 to mark the element whose
    inner HTML is captured for history snapshots.

## New Attributes

| Attribute | Purpose |
|---|---|
| `hx-status` | Per-status-code swap behavior |
| `hx-action` | Specify URL (use with `hx-method`) |
| `hx-method` | Specify HTTP method |
| `hx-config` | Per-element request config (replaces `hx-request`) |
| `hx-ignore` | Disable htmx processing (replaces `hx-disable`) |
| `hx-validate` | Control form validation behavior |

## New Extensions

htmx 4 ships with these core extensions. All auto-register when imported.

| Extension | Description |
|---|---|
| `browser-indicator` | Shows the browser's native loading indicator during requests |
| `optimistic` | Shows expected content from a template before the server responds |
| `upsert` | Update-or-insert swap strategy for dynamic lists |
| `download` | Save responses as file downloads with streaming progress |
| `targets` | Swap the same response into multiple elements |
| `history-cache` | Client-side history cache in `sessionStorage` |
| `ptag` | Per-element polling tags to skip unchanged content |
| `alpine-compat` | Alpine.js compatibility |
| `htmx-2-compat` | Backward compatibility layer for htmx 2.x code |
| `nonce` | CSP nonce-based protection for inline scripts and `eval`-style code paths (beta3) |
| `live` | DOM-reactivity via `hx-live` and richer `hx-on` helpers: `q()`, `toggle()`, `debounce()` (beta3) |

htmx also provides an `htmax` bundle (`htmax.min.js`) that includes htmx
plus the most popular extensions (SSE, WebSockets, preload,
browser-indicator, download, optimistic, targets) in a single file.

## JavaScript API Changes

**Removed methods** (use native JS):

| htmx 2.x | Use instead |
|---|---|
| `htmx.addClass()` | `element.classList.add()` |
| `htmx.removeClass()` | `element.classList.remove()` |
| `htmx.toggleClass()` | `element.classList.toggle()` |
| `htmx.closest()` | `element.closest()` |
| `htmx.remove()` | `element.remove()` |
| `htmx.off()` | `removeEventListener()` |
| `htmx.location()` | `htmx.ajax()` |
| `htmx.logAll()` | `htmx.config.logAll = true` |

**Renamed:** `htmx.defineExtension()` is now `htmx.registerExtension()`.

## Alpha to Beta1 Changes

If you are upgrading from an htmx 4 alpha release (not from v2), here is
what changed specifically between the alpha series and beta1:

- **`hx-on::` shorthand fixed**: The double-colon shorthand
  (e.g., `hx-on::before-request`) was broken in alpha8. It works correctly
  in beta1.
- **`globalViewTransitions` config removed**: Renamed to `transitions`.
  The old key is silently ignored. Remove any `<meta>` tags using the old
  name.
- **View transitions disabled by default**: No longer need the
  `{"globalViewTransitions": false}` workaround that was required in
  alpha2-alpha8.
- **SSE/WS extensions rewritten**: New APIs with per-element config,
  exponential backoff, `HX-Request-ID` correlation. See the upstream
  [SSE](https://four.htmx.org/docs/extensions/sse#upgrading-from-htmx-2x)
  and [WS](https://four.htmx.org/docs/extensions/ws#upgrading-from-htmx-2x)
  upgrade guides.
- **New extensions added**: `history-cache`, `ptag`, `targets`, `download`.
- **`htmax` bundle available**: Single-file bundle with htmx + popular
  extensions.

## Beta1 to Beta3 Changes

If you are upgrading from htmx 4 beta1 or beta2 (not from v2), here are
the changes specific to beta3 (which is the 4.0 release candidate).

### New Extensions

- **`hx-nonce`**: CSP nonce-based protection for inline scripts and
  `eval`-style code paths. Blocks elements without a matching `hx-nonce`
  attribute, integrates with TrustedTypes, and defends against
  `js:`/`javascript:` action URLs and unnonced boosted-form submitters.
  Vibetuner enforces nonce-based CSP by default, so this extension is a
  natural fit. See the
  [vibetuner CSP docs](development-guide.md#security-headers-and-csp-nonce).
- **`hx-live`**: DOM-reactivity via `hx-live="..."` (a JS expression
  re-evaluated whenever any DOM input/change/mutation event fires) plus
  a richer JavaScript surface inside `hx-on`: `q(selector)` jQuery-like
  proxy, sigil-syntax `toggle('@attr')` / `toggle('*display=none|block')`,
  per-element `debounce(ms[, fn])`, and `htmx.live.q` /
  `htmx.live.take(target, className, source)` outside expression scope.

### New Swap Style: `outerSync`

```html
<div hx-swap="outerSync"></div>
```

Copies attributes onto the existing target and replaces children. Useful
for clean `<body>` swaps in history replacement where you want to update
the body's attributes without losing the element identity.

### Restored Attribute: `hx-history-elt`

`hx-history-elt` is back. Mark the element whose inner HTML is captured
for history snapshots, the same as in htmx 2.

### Behavior Changes

- **`htmx.config.prefix` defaults to `"data-hx-"`**: Both `hx-*` and
  `data-hx-*` work out of the box, matching htmx 2 behavior. Set to
  `""` to disable the data-prefixed alias.
- **`htmx:response:error` event added**: Fires for HTTP 4xx/5xx
  responses, restoring the convenience of htmx 2's `htmx:responseError`.
- **`hx-download` auto-detection**: The `hx-download` extension now
  auto-detects downloads via the `Content-Disposition` response header,
  so you no longer need an `hx-download` attribute on each triggering
  element.
- **`hx-preload` boost knobs**: Added `boostEvent`, `boostTimeout`, and
  `autoBoost` config keys for tighter integration with `hx-boost`.

### Security Hardening

- **`hx-config` no longer accepts request `mode` overrides**: Removes a
  privilege-escalation surface where a swap could downgrade origin
  enforcement.
- **Constructable stylesheet for indicator CSS**: The runtime indicator
  CSS now uses a `CSSStyleSheet` constructor instead of an injected
  `<style>` tag, avoiding CSP `unsafe-inline` violations on
  `style-src`. With this change, CSP-strict deployments can drop
  `'unsafe-inline'` from `style-src` (Vibetuner is moving in this
  direction).
- **Pantry element switched from inline `style` to `hidden`**: Resolves
  another CSP `unsafe-inline` violation.

### Breaking JavaScript API Changes

`htmx.takeClass()` and `htmx.forEvent()` moved out of htmx core into
the new `hx-live` extension and are exposed via the `htmx.live`
namespace (e.g. `htmx.live.take(target, className, source)`). If you
were calling them directly, import the `hx-live` extension or migrate
to native equivalents.

## Common Migration Issues

### SSE elements stop updating after upgrade

**Symptom:** SSE-powered elements no longer receive updates.

**Cause:** The `hx-ext="sse"` attribute was removed but the SSE extension script is
still being loaded, conflicting with htmx v4's built-in SSE support.

**Fix:** Remove both the `hx-ext="sse"` attribute and any `<script>` tag loading
`htmx-ext-sse`. The `sse-connect` and `sse-swap` attributes work natively in v4.

### `window.htmx` is undefined in inline scripts

**Symptom:** Inline `<script>` tags or browser console show `htmx is not defined`.

**Cause:** htmx v4 uses a default export that must be explicitly assigned to `window`.

**Fix:** Update your JS entry point:

```javascript
import htmx from "@alltuner/vibetuner/htmx";
window.htmx = htmx;
```

### Attributes no longer inherited by child elements

**Symptom:** Buttons or links inside a container stop working because they relied on
a parent's `hx-target`, `hx-swap`, or similar attribute.

**Cause:** htmx v4 no longer inherits attributes by default.

**Fix:** Add `:inherited` to the parent attribute:

```html
<!-- Before: <div hx-target="#results"> -->
<div hx-target:inherited="#results">
```

### Preload extension not working

**Symptom:** `preload="mouseover"` has no effect after upgrade.

**Cause:** The import path changed and the old `hx-ext="preload"` is no longer needed.

**Fix:** Update your import and remove `hx-ext`:

```javascript
// Before: import "htmx-ext-preload";
import "@alltuner/vibetuner/htmx/preload";
```

```html
<!-- Before: <body hx-ext="preload"> -->
<body>
```

### `hx-vars` attribute ignored

**Symptom:** Dynamic values previously set via `hx-vars` are no longer sent.

**Cause:** `hx-vars` was removed in v4.

**Fix:** Use `hx-vals` with the `js:` prefix:

```html
<!-- Before: hx-vars="token:getToken()" -->
hx-vals='js:{"token": getToken()}'
```

### Error responses replacing page content unexpectedly

**Symptom:** A `422` or `500` response swaps error HTML into the page where it
previously was ignored.

**Cause:** htmx 4 swaps all HTTP responses by default.

**Fix:** Use `hx-status` for per-element control, or revert globally:

```javascript
htmx.config.noSwap = [204, 304, '4xx', '5xx'];
```

### Long-running requests timing out

**Symptom:** Requests that worked in v2 now fail after 60 seconds.

**Cause:** htmx 4 defaults to a 60-second timeout (v2 had no timeout).

**Fix:** Increase or disable the timeout:

```javascript
htmx.config.defaultTimeout = 0; // no timeout, like v2
```

## Migration Checklist

- [ ] Replace `hx-on::` shorthand with `hx-on:htmx:` long form, or upgrade
  to beta1+ where the shorthand works
- [ ] Replace `event.detail.successful` with `event.detail.ctx.response`
- [ ] Replace camelCase event names with colon-separated
  (e.g., `afterRequest` → `after:request`)
- [ ] Move `document.body` event listeners to the element or use `hx-on`
  attributes
- [ ] Remove all `hx-ext="sse"` attributes from SSE elements
- [ ] Remove all other `hx-ext="..."` attributes (extensions auto-register)
- [ ] Replace `hx-vars` with `hx-vals` using `js:` prefix
- [ ] Rename `hx-disable` to `hx-ignore`, then `hx-disabled-elt` to
  `hx-disable`
- [ ] Add `:inherited` modifier to attributes that rely on inheritance
- [ ] Update JS imports to use default import and `window.htmx = htmx`
- [ ] Update preload extension import path
- [ ] Remove `htmx-ext-sse` and `htmx-ext-preload` from `package.json`
  if present
- [ ] Rename config keys (`globalViewTransitions` → `transitions`, etc.)
- [ ] Remove any `{"globalViewTransitions": false}` meta tags
- [ ] Test error handling (4xx/5xx now swap by default)
- [ ] Test long-running requests against the 60-second timeout
- [ ] Update `hx-swap` scroll modifiers to new syntax if used
