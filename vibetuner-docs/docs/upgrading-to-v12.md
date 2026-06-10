# Upgrading to v12

This guide covers the breaking changes when upgrading a Vibetuner project
from v11 to v12. All three changes are security hardening: a fail-closed
session-key guard, autoescaping in the static-render template path, and a
default rate limit on the unauthenticated auth endpoints.

Most projects need only one action — set a real `SESSION_KEY` before
deploying to production. The other two changes are no-ops for the common
case (default email templates, normal auth traffic).

## Who's Affected / TL;DR Checklist

- [ ] **Every project deploying to production**: set a unique `SESSION_KEY`
  in `.env`. The app refuses to boot in production while the key is still a
  known placeholder. Generate one with `vibetuner crypto generate-key`.
- [ ] **Projects rendering custom HTML templates through
  `render_static_template`** that emit trusted, pre-rendered HTML: add an
  explicit `|safe` filter, or the markup now renders escaped. Projects using
  this only for the bundled transactional emails are unaffected.
- [ ] **Apps with heavy auth traffic, or tests that hammer the auth
  endpoints**: raise or disable `RATE_LIMIT_AUTH_LIMITS` (defaults to
  `5/minute` per IP).

If none of those apply to you, the upgrade is a version bump with no
code or config changes.

## Fail-Closed SESSION_KEY Guard

### What changed

`CoreConfiguration` now validates `session_key` at startup. When
`environment == "prod"` and the key is still a known placeholder, the app
raises a `ValueError` and refuses to start. Both placeholders are rejected:

- the historical default `ct-!secret-must-change-me`
- the current template default `CHANGE_ME_RUN_vibetuner_crypto_generate`

Outside production (`environment` defaults to `dev`), the app starts but
logs a loud warning instead, so local development stays friction-free.

### Why

Sessions are signed with `session_key`. A publicly-known placeholder lets
anyone forge a session cookie, so the value must be unique per deployment.
Failing closed in production turns a silent security hole into an obvious,
fix-before-deploy startup error.

### Action

Generate a fresh key and put it in your `.env`:

```bash
vibetuner crypto generate-key
```

This prints a URL-safe random key. Copy it into `.env`:

```bash
SESSION_KEY=<the-generated-key>
```

`generate-key` takes an optional `--length` / `-l` (number of random bytes,
default `32`) if you want a longer key.

### How to verify

With the placeholder still in place, a production start fails fast:

```bash
ENVIRONMENT=prod uv run vibetuner run prod
# ValueError: SESSION_KEY is still the placeholder value. Set a unique
# SESSION_KEY in your .env before running in production.
```

After setting a real `SESSION_KEY`, the app boots normally. In `dev` you
will see the warning go away once a non-placeholder key is set.

## Jinja Autoescaping in the Static-Render Path

### What changed

The Jinja `Environment` behind `render_static_template` (in
`vibetuner.templates`) now autoescapes by markup format. The decision keys
off the format extension underneath the `.jinja` wrapper:

- `*.html.jinja` and `*.xml.jinja` templates **are** escaped.
- `*.txt.jinja` templates (e.g. plain-text emails) are **not** escaped.

Rendering a bare string with no template name also defaults to escaping.

### Why

Without autoescaping, any context value interpolated with `{{ value }}` in
an HTML template is an injection vector. Escaping by default closes that
hole; plain-text templates stay unescaped because escaping there would
corrupt the output with HTML entities.

### Action

Only projects rendering **custom** templates through
`render_static_template` that emit **trusted, pre-rendered HTML** need to
act. If a value is intentionally HTML you produced (not user input), mark
it `|safe` so it renders verbatim:

```jinja
{# Before: rendered raw; now escaped #}
{{ prerendered_html }}

{# After: explicitly trusted #}
{{ prerendered_html | safe }}
```

Do **not** add `|safe` to values that can contain user input — that
reintroduces the injection risk autoescaping exists to prevent.

The bundled transactional email templates are unaffected, so projects that
use this path only for the default emails need no changes.

### How to verify

Render a custom HTML template that interpolates a value containing markup
(e.g. `<b>hi</b>`). Without `|safe` it now renders as escaped entities
(`&lt;b&gt;hi&lt;/b&gt;`); with `|safe` on a value you trust, it renders as
live markup.

## Default Auth Rate Limits

### What changed

`POST /auth/magic-link-login` and the OAuth-init endpoint now default to
`5/minute` per IP. The limit is configured by `RateLimitSettings.auth_limits`
(env var `RATE_LIMIT_AUTH_LIMITS`).

### Why

The unauthenticated auth endpoints are an email-flooding and account
enumeration surface. A modest per-IP cap curbs abuse without affecting
real users, who hit these endpoints a handful of times at most.

### Action

Only if you need it. Apps with legitimately high auth traffic, or test
suites that exercise these endpoints repeatedly, can raise or disable the
limit via the environment:

```bash
# Raise the limit
RATE_LIMIT_AUTH_LIMITS=60/minute

# Effectively disable it (very high ceiling)
RATE_LIMIT_AUTH_LIMITS=10000/minute
```

The string follows slowapi's format (`"X per Y"` or `"X/Y"`, where `Y` is
`second`, `minute`, `hour`, or `day`).

### How to verify

Send more than five magic-link requests from the same IP within a minute;
the sixth returns `429 Too Many Requests`. After raising
`RATE_LIMIT_AUTH_LIMITS`, the higher ceiling applies.

## See Also (no action required)

- **Cache invalidation has a public `invalidate()`**: use
  `invalidate(path, *, query_params="", vary=None)` from `vibetuner.cache`
  instead of importing the private `_build_cache_key`. The `vary` argument
  targets an entry written for a route cached with `vary_on`. See
  [Rate Limiting](rate-limiting.md) and the caching docs in the
  [Development Guide](development-guide.md).
- **Pick up template improvements**: run `vibetuner scaffold update` to pull
  in template and tooling updates (for example the new `dprint.json`).

## Migration Checklist

- [ ] Run `vibetuner crypto generate-key` and set a unique `SESSION_KEY` in
  `.env` before deploying to production
- [ ] If you render custom HTML templates through `render_static_template`
  that emit trusted pre-rendered HTML, add `|safe` to those values
- [ ] If you have high auth traffic or tests that hammer the auth endpoints,
  set `RATE_LIMIT_AUTH_LIMITS` to a suitable value
- [ ] (Optional) Replace any imports of the private `_build_cache_key` with
  the public `invalidate(...)`
- [ ] (Optional) Run `vibetuner scaffold update` to pick up template
  improvements
