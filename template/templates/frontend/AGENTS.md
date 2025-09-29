# Template System

Layered Jinja2 template system with automatic fallback.

## Template Loading

1. `templates/frontend/` (your templates)
2. `templates/frontend/defaults/` (scaffolding fallback)

## Overriding Templates

Copy from `defaults/` to parent directory:

```bash
# Override footer
cp templates/frontend/defaults/base/footer.html.jinja \
   templates/frontend/base/footer.html.jinja

# Now edit templates/frontend/base/footer.html.jinja
```

## Template Rendering

```python
from ..templates import render_template

def render_template(
    template: str,           # e.g., "index.html.jinja"
    request: Request,
    ctx: dict | None = None,
    **kwargs
) -> HTMLResponse
```

## Available Filters

- `{{ datetime | timeago }}` - "2 hours ago"
- `{{ datetime | format_date }}` - "January 15, 2024"
- `{{ text | markdown }}` - Convert Markdown to HTML
- `{{ text | sanitize_and_format }}` - Sanitize HTML, auto-link

## Global Variables

- `DEBUG` - Debug mode flag
- `hotreload` - Dev hot-reload script
- `request` - FastAPI Request object

## Template Inheritance

```jinja
{% extends "base/skeleton.html.jinja" %}

{% block title %}My Page{% endblock %}

{% block content %}
<div class="container mx-auto">
    <h1>Content here</h1>
</div>
{% endblock %}
```

## Best Practices

1. Never modify `defaults/` - override by copying
2. Use template inheritance for consistency
3. Keep overrides minimal
4. Use `.html.jinja` extension
