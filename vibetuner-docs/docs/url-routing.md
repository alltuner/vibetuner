# URL Routing with Sub-Mounted Apps

Starlette (and FastAPI) supports referencing routes in mounted sub-applications using
the `url_for('mount_name:route_name')` syntax. This works in both Python code and
Jinja templates.

## How It Works

When you mount a sub-application with `app.mount()`, the `name` parameter defines
the prefix used in `url_for`:

```python
app.mount("/some-path", app=sub_app, name="myapp")

# Now accessible as:
url_for("myapp:route_name")
```

The mount path (`/some-path`) and the name (`myapp`) are independent — the name is
what you use in `url_for`, not the path.

## Built-in Mounted Apps

Vibetuner automatically mounts several sub-applications. Here are the ones available
for `url_for`:

| App | Mount Name | Path | Condition |
|-----|-----------|------|-----------|
| CSS static files | `css` | `/static/v{hash}/css` | Always |
| JS static files | `js` | `/static/v{hash}/js` | Always |
| Image static files | `img` | `/static/v{hash}/img` | Always |
| Favicon files | `favicons` | `/static/favicons` | Always |
| Font files | `fonts` | `/static/fonts` | Always |

### Static Files

Static file mounts use the `path` parameter:

```jinja
<link rel="stylesheet" href="{{ url_for('css', path='bundle.css').path }}">
<script src="{{ url_for('js', path='bundle.js').path }}"></script>
<img src="{{ url_for('img', path='logo.png').path }}">
```

## Mounting Your Own Sub-Apps

You can mount additional sub-applications in your `tune.py`:

```python
from starlette.applications import Starlette

# Create a sub-app
api_v2 = Starlette()

@api_v2.route("/users")
async def api_users(request):
    ...

# In your tune.py app configuration, mount it:
app.mount("/api/v2", app=api_v2, name="api_v2")
```

Then reference its routes:

```jinja
<a href="{{ url_for('api_v2:api_users') }}">API Users</a>
```

!!! important "The `name` parameter is required"
    Without `name=` on `app.mount()`, the sub-app's routes won't be
    accessible via `url_for`.

## Why Use `url_for` Instead of Hardcoded URLs

- **Resilience**: Links stay correct if route prefixes change
- **Linting**: djlint rule J018 catches hardcoded URLs in templates
- **Consistency**: All internal links follow the same pattern
- **Refactoring**: Rename paths in one place, not across all templates
