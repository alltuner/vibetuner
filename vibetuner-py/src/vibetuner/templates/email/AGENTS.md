# Core Email Templates - DO NOT MODIFY

**⚠️ IMPORTANT**: Package-managed files. Changes will be lost on package updates.

## How to Override

**NEVER modify files in this directory!** Instead:

1. Copy template to your project's `templates/email/`
2. Maintain the same directory structure
3. Your version overrides automatically

### Example

```bash
# Core template (DO NOT EDIT, bundled in vibetuner package):
vibetuner/templates/email/default/magic_link.html.jinja

# Your override (CREATE THIS in your project):
templates/email/default/magic_link.html.jinja
```

## Template Structure

```text
vibetuner/email/
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
