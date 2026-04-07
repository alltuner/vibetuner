---
paths:
  - .env*
  - src/*/config*
  - src/*/tune.py
description: Environment variables, settings, security headers, and request ID
---

# Configuration

**Env vars** (`.env`, not committed): `DATABASE_URL`, `REDIS_URL`,
`SECRET_KEY`, `DEBUG`.

**Settings**: `from vibetuner.config import settings` —
`.environment`, `.debug`, `.resolved_port`, `.expose_url`,
`.mongodb_url`, `.redis_url`, `.workers_available`,
`.project.project_slug`, `.project.project_name`,
`.project.supported_languages`, `.project.default_language`,
`.project.fqdn`.

## Security Headers

CSP with nonce-based scripts enabled by default. The CSP nonce is
auto-injected into all `<script>` tags in HTML responses, so you
don't need to add it manually. For `<style>` tags, use
`{{ csp_nonce }}` template variable. Debug mode = report-only.
Configure via `CSP_*` env vars. Avoid inline event handlers
(`onclick` etc.) — use HTMX attributes or `addEventListener`.

## Request ID

Auto-assigned `X-Request-ID` (UUID4), reuses incoming header if
present. Access via `vibetuner.frontend.request_id.get_request_id()`
or `request_id_dependency`.
