
# Default Templates - DO NOT MODIFY

**⚠️ IMPORTANT**: These templates are managed by the scaffolding system and
should NEVER be modified directly.

## Why These Files Are Protected

- Maintained by the scaffolding template
- Updates come through `just update-scaffolding`
- Manual changes will be lost on scaffolding updates
- Breaking changes can corrupt the application's UI

## How to Override Templates

**NEVER modify files in this directory!** Instead:

1. Copy the template you want to customize
2. Place it in the parent directory (`templates/frontend/`)
3. Remove the `defaults/` part from the path
4. Your custom version will automatically override the default

### Example: Customizing the Footer

Default location:

```text
templates/frontend/defaults/base/footer.html.jinja  ← DO NOT EDIT
```

Your override:

```text
templates/frontend/base/footer.html.jinja  ← CREATE THIS
```

## Default Template Structure

```text
defaults/
├── base/               # Core layout components
│   ├── skeleton.html.jinja    # Main HTML structure
│   ├── header.html.jinja      # Navigation header
│   └── footer.html.jinja      # Page footer
├── debug/              # Development tools
├── email/              # Email templates
├── user/               # User management pages
├── index.html.jinja    # Homepage
├── login.html.jinja    # Authentication
└── email_sent.html.jinja  # Email confirmation
```

## If You Need Core Changes

### Scenario 1: Missing Template Variables

If a default template lacks needed variables:

1. Override the template with your custom version
2. Pass additional context from your route handler
3. Consider if it's a scaffolding limitation worth reporting

### Scenario 2: Structural Changes Needed

For fundamental template structure changes:

1. **Document the limitation** for the user
2. **Suggest**: "This requires scaffolding customization. Options:
   - Override the entire template hierarchy
   - Fork and customize the scaffolding
   - File an issue for the enhancement"

## Common Override Patterns

### Adding to Base Layout

Override `base/skeleton.html.jinja` to:

- Add custom meta tags
- Include additional CSS/JS
- Modify the overall structure

### Customizing Navigation

Override `base/header.html.jinja` to:

- Add menu items
- Change branding
- Modify user dropdown

### Extending Forms

Override authentication templates to:

- Add fields to registration
- Customize login flow
- Modify email templates

## Best Practices

1. **Minimal overrides**: Only override what you need to change
2. **Track changes**: Document why each override exists
3. **Test updates**: After `just update-scaffolding`, verify overrides still work
4. **Use inheritance**: Extend base templates rather than duplicating

## Getting Help

If blocked by default template limitations:

1. First try the override mechanism
2. Check if you can achieve it with HTMX/Alpine.js
3. Consider if it belongs in application templates instead
4. Suggest improvements to the scaffolding repository
