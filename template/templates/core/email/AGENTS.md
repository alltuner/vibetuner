# Core Email Templates - DO NOT MODIFY

**⚠️ IMPORTANT**: Scaffolding-managed files. Changes will be lost on updates.

## How to Override

**NEVER modify files in this directory!** Instead:

1. Copy template to `templates/app/email/`
2. Maintain the same directory structure
3. Your version overrides automatically

### Example

```bash
# Core template (DO NOT EDIT):
templates/core/email/default/magic_link.html.jinja

# Your override (CREATE THIS):
templates/app/email/default/magic_link.html.jinja
```

## Template Structure

```text
core/email/
└── default/
    ├── magic_link.html.jinja  # Passwordless login email (HTML)
    └── magic_link.txt.jinja   # Passwordless login email (text)
```

## Magic Link Email

The core provides magic link authentication emails used by the auth system.

### Variables Available

- `login_url` - The magic link URL for authentication
- `project_name` - Your project's display name

Override these templates to customize branding, styling, and content.

## Best Practices

1. Always provide both HTML and text versions
2. Test overrides after scaffolding updates
3. Keep branding consistent across all emails
4. Use inline styles for HTML emails
