# HTMX v2 to v4 Migration Guide

This guide covers the breaking changes when upgrading from htmx v2 to v4
in Vibetuner projects.

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

The `sse-connect` and `sse-swap` attributes work exactly the same — just remove
`hx-ext="sse"` from the element.

## Extension Auto-Registration

In v2, extensions had to be explicitly activated via `hx-ext="..."` on each element
or a parent. In v4, extensions auto-register when imported — no `hx-ext` attribute
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

**Before (v2):**

```html
<div hx-disable>
    <a href="/page">Regular link, not processed by htmx</a>
</div>
```

**After (v4):**

```html
<div hx-ignore>
    <a href="/page">Regular link, not processed by htmx</a>
</div>
```

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

## JavaScript Import Changes

htmx v4 uses a default export. The import pattern in your `config.js` (or equivalent
entry point) must be updated.

**Before (v2):**

```javascript
import "htmx.org";
```

**After (v4):**

```javascript
import htmx from "htmx.org";
window.htmx = htmx;
```

The default import is required, and you must explicitly assign `htmx` to `window` for
it to be available globally (e.g., in inline scripts or the browser console).

### Preload Extension

The preload extension moved from a separate package to a built-in module.

**Before (v2):**

```javascript
import "htmx-ext-preload";
```

**After (v4):**

```javascript
import "htmx.org/dist/ext/hx-preload.js";
```

## Event Names Changed from camelCase to Colon-Separated

All htmx event names switched from camelCase to colon-separated format.

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
element.addEventListener("htmx:after:settle", handler);
```

!!! warning
    Events no longer bubble to `document.body` in v4. You must attach listeners
    directly to the element or use `hx-on` attributes. Delegation patterns like
    `document.body.addEventListener('htmx:after:request', ...)` do not work.

## Event Handler Attributes (`hx-on`)

The `hx-on::` shorthand (e.g., `hx-on::after-request`) is broken in htmx 4.0.0-alpha8.
It registers a listener for `:after-request`, but the dispatched event is
`htmx:after:request`. Use the explicit long form instead.

**Before (v2):**

```html
<form hx-on::after-request="if(event.detail.successful) this.reset()">
```

**After (v4):**

```html
<form hx-on:htmx:after:request="this.reset()">
```

!!! note
    The `hx-on::` shorthand may be fixed in a future htmx release, but the long
    form `hx-on:htmx:after:request` works reliably and is the recommended approach.

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

## View Transitions Disabled

htmx v4 initially shipped with CSS view transitions enabled by default, which
caused ~500ms UI blocking after each request
([htmx#3566](https://github.com/bigskysoftware/htmx/issues/3566)). The htmx
team disabled transitions as the default in a later release.

Vibetuner's skeleton template includes a `<meta>` tag that explicitly disables
them for compatibility with alpha8:

```html
<meta name="htmx-config" content='{"globalViewTransitions": false}' />
```

If you want view transitions, remove this tag and add CSS transition rules
per the [htmx view transitions docs](https://four.htmx.org).

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
import htmx from "htmx.org";
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
import "htmx.org/dist/ext/hx-preload.js";
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

## Migration Checklist

- [ ] Replace `hx-on::` shorthand with `hx-on:htmx:` long form
- [ ] Replace `event.detail.successful` with `event.detail.ctx.response`
- [ ] Replace camelCase event names with colon-separated (e.g., `afterRequest` → `after:request`)
- [ ] Move `document.body` event listeners to the element or use `hx-on` attributes
- [ ] Remove all `hx-ext="sse"` attributes from SSE elements
- [ ] Remove all other `hx-ext="..."` attributes (extensions auto-register)
- [ ] Replace `hx-vars` with `hx-vals` using `js:` prefix
- [ ] Replace `hx-disable` with `hx-ignore`
- [ ] Add `:inherited` modifier to attributes that rely on inheritance
- [ ] Update JS imports to use default import and `window.htmx = htmx`
- [ ] Update preload extension import path
- [ ] Remove `htmx-ext-sse` and `htmx-ext-preload` from `package.json` if present
