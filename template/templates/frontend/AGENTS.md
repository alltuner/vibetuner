# Application Frontend Templates

YOUR CUSTOM TEMPLATES GO HERE

## Purpose

This directory contains your application-specific frontend templates and overrides
of core templates.

## Override System

Templates in this directory automatically override core templates with the same path:

```bash
# Core template (scaffolding default):
templates/vibetuner/frontend/base/footer.html.jinja

# Your override (searches first):
templates/app/frontend/base/footer.html.jinja
```

## Directory Structure

Match the structure from `templates/vibetuner/frontend/` when overriding:

```text
app/frontend/
├── base/               # Layout overrides
│   ├── skeleton.html.jinja
│   ├── header.html.jinja
│   └── footer.html.jinja
├── user/               # User page overrides
├── custom/             # Your custom templates
│   ├── dashboard.html.jinja
│   └── ...
└── index.html.jinja    # Homepage override
```

## Usage

### Creating New Templates

```jinja
{# templates/app/frontend/dashboard/home.html.jinja #}
{% extends "base/skeleton.html.jinja" %}

{% block title %}Dashboard{% endblock %}

{% block content %}
<div class="container mx-auto p-4">
  <h1 class="text-2xl font-bold">Welcome, {{ user.name }}</h1>
  {# Your content here #}
</div>
{% endblock %}
```

### Overriding Core Templates

```bash
# 1. Copy the core template
cp templates/vibetuner/frontend/base/header.html.jinja \
   templates/app/frontend/base/header.html.jinja

# 2. Edit your copy
# templates/app/frontend/base/header.html.jinja
```

### Rendering from Routes

```python
from vibetuner.frontend.templates import render_template

@router.get("/dashboard")
async def dashboard(request: Request):
    # Automatically uses templates/app/frontend/dashboard/home.html.jinja
    # if it exists, otherwise falls back to templates/vibetuner/frontend/
    return render_template("dashboard/home.html.jinja", request, {
        "user": current_user,
        "stats": dashboard_stats
    })
```

## Best Practices

1. **Extend, don't duplicate**: Use `{% extends %}` and `{% block %}` to
   build on core templates
2. **Organize by feature**: Group related templates in subdirectories
3. **Document overrides**: Add comments explaining why you're overriding
4. **Test fallbacks**: Ensure your overrides work after scaffolding updates
5. **Minimal overrides**: Only override what you need to change

## Available Template Variables

All templates automatically receive:

- `request` - Current request object
- `DEBUG` - Debug mode flag
- `hotreload` - Hot reload function (dev mode)
- Project settings from configuration
- Current language/locale info

## Template Inheritance

Core provides these base templates:

- `base/skeleton.html.jinja` - Main layout with head, body structure
- `base/header.html.jinja` - Navigation header
- `base/footer.html.jinja` - Page footer
- `base/opengraph.html.jinja` - OpenGraph meta tags
- `base/favicons.html.jinja` - Favicon links

Extend them in your templates:

```jinja
{% extends "base/skeleton.html.jinja" %}

{% block extra_head %}
  {# Add page-specific CSS/JS #}
{% endblock %}

{% block content %}
  {# Your page content #}
{% endblock %}
```
