---
paths:
  - locales/**
  - babel.cfg
description: i18n, translations, and locale management
---

# Localization

```bash
just i18n                    # Full workflow
just new-locale LANG         # New language
```

Templates: `{% trans %}Welcome{% endtrans %}`.
Python: `from starlette_babel import gettext_lazy as _`.

## Language switcher (Jinja)

`language_picker()` is registered as a Jinja global. It returns
`[{code, name}]` with names rendered in the **current request locale**
(browsing in Spanish gives "inglés / español / catalán").

```jinja
<select name="language">
    {% for entry in language_picker() %}
        <option value="{{ entry.code }}"
                {% if entry.code == language %}selected{% endif %}>
            {{ entry.name }}
        </option>
    {% endfor %}
</select>
```

Pass an explicit locale to override: `{% for e in language_picker("es") %}`.

## Forcing a language mid-request

After login or a tenant switch, use `set_request_language` so
`{% trans %}`, `<html lang>` and `Content-Language` stay in sync:

```python
from vibetuner.i18n import set_request_language

set_request_language(request, user.preferred_language)
```

## Custom locale resolvers (per-tenant, per-domain)

Register a resolver to inject a custom selector at the front of the
locale chain. Returns a code or `None` to defer:

```python
from vibetuner.i18n import register_locale_resolver

def tenant_locale(conn):
    tenant = conn.scope.get("state", {}).get("tenant")
    return tenant.language if tenant else None

register_locale_resolver(tenant_locale)
```

Resolvers must be synchronous; do DB lookups in upstream middleware.
Fail-soft: a raising resolver is logged and the chain falls through.

Full reference:
<https://vibetuner.alltuner.com/development-guide/#custom-locale-resolvers-register_locale_resolver>
