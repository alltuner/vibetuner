# Default Templates - DO NOT MODIFY

**⚠️ IMPORTANT**: Scaffolding-managed files. Changes will be lost on updates.

## How to Override

**NEVER modify files in this directory!** Instead:

1. Copy template to parent directory (`templates/frontend/`)
2. Remove `defaults/` from path
3. Your version overrides automatically

### Example

```bash
# Default (DO NOT EDIT):
templates/frontend/defaults/base/footer.html.jinja

# Your override (CREATE THIS):
templates/frontend/base/footer.html.jinja
```

## Default Structure

```text
defaults/
├── base/               # Core layout
│   ├── skeleton.html.jinja
│   ├── header.html.jinja
│   └── footer.html.jinja
├── debug/              # Dev tools
├── email/              # Email templates
├── user/               # User pages
├── index.html.jinja
├── login.html.jinja
└── email_sent.html.jinja
```

## Common Overrides

- `base/skeleton.html.jinja` - Add meta tags, CSS/JS
- `base/header.html.jinja` - Customize navigation
- `base/footer.html.jinja` - Custom footer

## Best Practices

1. Minimal overrides only
2. Document why each override exists
3. Test after `just update-scaffolding`
4. Use template inheritance
