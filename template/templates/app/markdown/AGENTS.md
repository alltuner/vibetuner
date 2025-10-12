# Application Markdown Templates

YOUR CUSTOM MARKDOWN TEMPLATES GO HERE

## Purpose

This directory contains your application-specific markdown templates.

## Override System

Templates in this directory automatically override core markdown templates:

```bash
# Core template (if any):
templates/core/markdown/default/terms.md.jinja

# Your override (searches first):
templates/app/markdown/default/terms.md.jinja
```

## Directory Structure

Markdown templates follow the same language-based structure as email templates:

```text
app/markdown/
├── default/            # Default language templates
│   ├── terms.md.jinja
│   ├── privacy.md.jinja
│   └── changelog.md.jinja
├── en/                 # English-specific templates
│   └── terms.md.jinja
└── es/                 # Spanish-specific templates
    └── terms.md.jinja
```

## Usage

### Creating Markdown Templates

```jinja
{# templates/app/markdown/default/terms.md.jinja #}
# Terms of Service

Last updated: {{ last_updated }}

## 1. Acceptance of Terms

By accessing {{ project_name }}, you agree to these terms.

## 2. Use License

...
```

### Rendering Markdown Templates

```python
from core.templates import render_static_template
import markdown

def get_terms_content(lang: str = "en") -> str:
    """Render terms of service as HTML."""
    md_content = render_static_template(
        "terms.md",
        namespace="markdown",
        lang=lang,
        context={
            "project_name": "My App",
            "last_updated": "2024-01-01"
        }
    )
    
    # Convert markdown to HTML
    html_content = markdown.markdown(md_content)
    return html_content
```

## Common Use Cases

- Terms of Service
- Privacy Policy
- Documentation pages
- Help articles
- Changelog
- Release notes
- Blog posts

## Best Practices

1. **Use frontmatter**: Add metadata at the top of templates
2. **Localization**: Create language-specific versions
3. **Keep it simple**: Standard markdown syntax
4. **Variables**: Use Jinja2 for dynamic content
5. **Versioning**: Include last updated dates
