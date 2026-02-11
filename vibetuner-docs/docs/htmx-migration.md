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

## Migration Checklist

- [ ] Remove all `hx-ext="sse"` attributes from SSE elements
- [ ] Remove all other `hx-ext="..."` attributes (extensions auto-register)
- [ ] Replace `hx-vars` with `hx-vals` using `js:` prefix
- [ ] Replace `hx-disable` with `hx-ignore`
- [ ] Add `:inherited` modifier to attributes that rely on inheritance
- [ ] Update JS imports to use default import and `window.htmx = htmx`
- [ ] Update preload extension import path
- [ ] Remove `htmx-ext-sse` and `htmx-ext-preload` from `package.json` if present
