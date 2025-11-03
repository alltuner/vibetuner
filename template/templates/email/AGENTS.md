# Application Email Templates

YOUR CUSTOM EMAIL TEMPLATES GO HERE

## Purpose

This directory contains your application-specific email templates and overrides
of core email templates from the vibetuner package.

## Override System

Templates in this directory automatically override core email templates:

```bash
# Core template (bundled in vibetuner package):
vibetuner/templates/email/default/magic_link.html.jinja

# Your override (searches first):
templates/email/default/magic_link.html.jinja
```

## Directory Structure

Email templates follow a language-based structure:

```text
email/
├── default/            # Default language templates
│   ├── welcome.html.jinja
│   ├── welcome.txt.jinja
│   ├── magic_link.html.jinja    # Override core magic link
│   └── magic_link.txt.jinja
├── en/                 # English-specific templates
│   ├── welcome.html.jinja
│   └── welcome.txt.jinja
└── es/                 # Spanish-specific templates
    ├── welcome.html.jinja
    └── welcome.txt.jinja
```

The system searches:

1. `templates/email/{lang}/` (your language-specific)
2. `templates/email/default/` (your default)
3. `vibetuner/templates/email/{lang}/` (package language-specific)
4. `vibetuner/templates/email/default/` (package default)

## Usage

### Creating Email Templates

Always provide both HTML and text versions:

```jinja
{# templates/email/default/welcome.html.jinja #}
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Welcome to {{ project_name }}</title>
</head>
<body style="font-family: Arial, sans-serif; padding: 20px;">
  <h1>Welcome, {{ user_name }}!</h1>
  <p>Thank you for joining {{ project_name }}.</p>
  <p>
    <a href="{{ dashboard_url }}"
       style="background: #007bff; color: white; padding: 10px 20px;
              text-decoration: none; border-radius: 5px;">
      Get Started
    </a>
  </p>
</body>
</html>
```

```jinja
{# templates/email/default/welcome.txt.jinja #}
Welcome to {{ project_name }}, {{ user_name }}!

Thank you for joining {{ project_name }}.

Get started: {{ dashboard_url }}
```

### Sending Emails

```python
from vibetuner.templates import render_static_template
from vibetuner.services.email import SESEmailService

async def send_welcome_email(user_email: str, user_name: str, lang: str = "en"):
    html_body = render_static_template(
        "welcome.html",
        namespace="email",
        lang=lang,
        context={
            "user_name": user_name,
            "project_name": "My App",
            "dashboard_url": "https://example.com/dashboard"
        }
    )

    text_body = render_static_template(
        "welcome.txt",
        namespace="email",
        lang=lang,
        context={
            "user_name": user_name,
            "project_name": "My App",
            "dashboard_url": "https://example.com/dashboard"
        }
    )

    ses_service = SESEmailService()
    await ses_service.send_email(
        subject=f"Welcome to My App!",
        html_body=html_body,
        text_body=text_body,
        to_address=user_email
    )
```

## Best Practices

1. **Always provide text version**: Not all email clients support HTML
2. **Inline styles**: Use inline CSS for email HTML
3. **Test rendering**: Check in multiple email clients
4. **Keep it simple**: Avoid complex layouts
5. **Localization**: Create language-specific versions when needed
6. **Subject lines**: Make them clear and actionable

## Core Email Templates

The vibetuner package provides:

- `magic_link.html.jinja` / `magic_link.txt.jinja` - Passwordless login emails

Override these by copying to your `templates/email/` directory.

## Localization

For multi-language emails:

```bash
# Create language-specific versions
templates/email/
├── default/        # Fallback
│   └── welcome.html.jinja
├── en/            # English
│   └── welcome.html.jinja
└── es/            # Spanish
    └── welcome.html.jinja
```

The system automatically selects the appropriate language version based on the
`lang` parameter passed to `render_static_template()`.
