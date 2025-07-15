# Template System Documentation

## Overview

This application uses a layered Jinja2 template system with automatic fallback support. Templates in this directory (`templates/frontend/`) can override default templates provided by the scaffolding.

## Template Loading Order

The system uses a two-tier template lookup system defined in `src/castuner/core/paths.py`:

1. **Primary Path**: `templates/frontend/`
2. **Fallback Path**: `templates/frontend/defaults/`

When a template is requested, the system:

1. First looks in `templates/frontend/`
2. If not found, falls back to `templates/frontend/defaults/`

This is implemented via the `to_template_path_list()` function which creates a list of paths that Jinja2's FileSystemLoader searches in order.

## Directory Structure

### `defaults/` (Scaffolding-Provided Templates)

These templates are provided by the scaffolding and should NOT be modified directly:

- `base/skeleton.html.jinja` - Base HTML layout with HTMX
- `base/footer.html.jinja` - Default footer component
- `base/header.html.jinja` - Default header component
- `index.html.jinja` - Default homepage
- `login.html.jinja` - Authentication page
- `email_sent.html.jinja` - Email confirmation page
- `debug/` - Development debugging templates
- `email/` - Email templates (magic link)
- `lang/` - Language selection components

### Custom Templates (Your Override Directory)

Place your custom templates directly in `templates/frontend/` to override defaults:

```text
templates/frontend/
├── base/              # Override base templates
└── index.html.jinja   # Custom homepage (overrides default)
```

## How to Override Templates

To override a default template:

1. Create the same file path in `templates/frontend/` (without the `defaults/` part)
2. The custom template will automatically take precedence

### Example: Override the default footer

Default template location:

```text
templates/frontend/defaults/base/footer.html.jinja
```

Your override location:

```text
templates/frontend/base/footer.html.jinja
```

## Template Rendering

Templates are rendered using the `render_template()` function from `src/castuner/frontend/templates.py`:

```python
def render_template(
    template: str,
    request: Request,
    ctx: dict[str, Any] | None = None,
    **kwargs: Any,
) -> HTMLResponse
```

The function:

- Merges context data with the request object
- Uses the Jinja2Templates instance configured with the path list
- Returns an HTMLResponse

## Available Jinja2 Filters

The following custom filters are available in templates:

- `markdown` - Convert Markdown text to HTML
- `timeago` - Convert datetime to human-readable time (e.g., "2 hours ago")
- `duration` - Format seconds as MM:SS
- `sanitize_and_format` - Sanitize HTML and format plain text with auto-linking

## Global Template Variables

- `DEBUG` - Boolean indicating if debug mode is active
- `hotreload` - Hot reload functionality for development
- `request` - The current FastAPI request object

## Best Practices

1. **Never modify files in `defaults/`** - These are managed by the scaffolding
2. **Use template inheritance** - Extend `base/skeleton.html.jinja` for consistent layout
3. **Keep overrides minimal** - Only override what you need to change
4. **Follow naming conventions** - Use `.html.jinja` extension for all templates
5. **Organize by feature** - Group related templates in subdirectories

## Template Inheritance Example

To create a new page that extends the base layout:

```jinja
{% extends "base/skeleton.html.jinja" %}

{% block title %}My Custom Page{% endblock %}

{% block content %}
<div class="container mx-auto">
    <h1>Welcome to My Custom Page</h1>
    <!-- Your content here -->
</div>
{% endblock %}
```

## Debugging Template Loading

To debug which template is being loaded:

1. Check if your custom template exists in `templates/frontend/`
2. If not found, the system will use the default from `templates/frontend/defaults/`
3. Template not found errors will show the full search path

Remember: The fallback mechanism ensures the application always has working templates while allowing complete customization.
