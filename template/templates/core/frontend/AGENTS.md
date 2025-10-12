# Core Frontend Templates - DO NOT MODIFY

**⚠️ IMPORTANT**: Scaffolding-managed files. Changes will be lost on updates.

## How to Override

**NEVER modify files in this directory!** Instead:

1. Copy template to `templates/app/frontend/`
2. Maintain the same directory structure
3. Your version overrides automatically

### Example

```bash
# Core template (DO NOT EDIT):
templates/core/frontend/base/footer.html.jinja

# Your override (CREATE THIS):
templates/app/frontend/base/footer.html.jinja
```

The template system searches in order:
1. `templates/app/frontend/` (your overrides)
2. `templates/core/frontend/` (scaffolding defaults)

## Template Structure

```text
core/frontend/
├── base/               # Core layout
│   ├── skeleton.html.jinja
│   ├── header.html.jinja
│   ├── footer.html.jinja
│   ├── opengraph.html.jinja
│   └── favicons.html.jinja
├── debug/              # Dev tools (DEBUG mode only)
│   ├── index.html.jinja
│   ├── info.html.jinja
│   ├── users.html.jinja
│   ├── collections.html.jinja
│   └── version.html.jinja
├── email/              # Email-related pages
│   └── magic_link templates
├── lang/               # Language switcher
│   └── select.html.jinja
├── meta/               # SEO and meta files
│   ├── robots.txt.jinja
│   ├── sitemap.xml.jinja
│   ├── site.webmanifest.jinja
│   └── browserconfig.xml.jinja
├── user/               # User account pages
│   ├── profile.html.jinja
│   └── edit.html.jinja
├── index.html.jinja        # Default homepage
├── login.html.jinja        # Login page
└── email_sent.html.jinja   # Magic link sent confirmation
```

## Common Overrides

- `base/skeleton.html.jinja` - Add meta tags, global CSS/JS
- `base/header.html.jinja` - Customize navigation
- `base/footer.html.jinja` - Custom footer
- `index.html.jinja` - Custom homepage

## Best Practices

1. Override only what you need
2. Document why each override exists
3. Test after `just update-scaffolding`
4. Use template inheritance and blocks
5. Keep overrides minimal to ease updates
