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
