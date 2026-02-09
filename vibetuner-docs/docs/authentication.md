# Authentication

Vibetuner provides built-in authentication with OAuth and magic links.

!!! note "Package name convention"
    In all examples, `app` refers to your project's Python package (the directory under `src/`).
    The actual name depends on your project slug (e.g., `src/myproject/` for a project named
    "myproject").

## Overview

Vibetuner includes:

- **OAuth Authentication**: Google, GitHub, and more via Authlib
- **Magic Link Authentication**: Passwordless email-based login
- **Session Management**: Secure cookie-based sessions
- **User Model**: Pre-configured with OAuth account linking

## OAuth Setup

### Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URI: `http://localhost:8000/auth/google/callback`

Add to `.env`:

```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

### GitHub OAuth

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Create a new OAuth App
3. Set callback URL: `http://localhost:8000/auth/github/callback`

Add to `.env`:

```bash
GITHUB_CLIENT_ID=your-client-id
GITHUB_CLIENT_SECRET=your-client-secret
```

### Adding More Providers

Vibetuner uses [Authlib](https://authlib.org/) which supports many OAuth providers.
To add additional providers, file an issue at [github.com/alltuner/vibetuner](https://github.com/alltuner/vibetuner/issues)
or extend authentication in your `src/app/` code.

## Magic Link Authentication

Magic links provide passwordless authentication via email.

### Configuration

Magic links are enabled by default. Configure email settings:

```bash
# .env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@example.com
```

### How It Works

1. User enters email address
2. System sends email with unique token
3. User clicks link in email
4. System validates token and logs user in
5. Session created

### Customizing Email Templates

Edit `templates/emails/magic_link.html.jinja`:

```html
<!DOCTYPE html>
<html>
    <body>
        <h1>Sign in to {{ app_name }}</h1>
        <p>Click the link below to sign in:</p>
        <a href="{{ magic_link }}">Sign In</a>
        <p>This link expires in 15 minutes.</p>
    </body>
</html>
```

## User Model

The built-in User model supports both OAuth and magic link authentication:

```python
# vibetuner.models.user
class User(Document):
    email: str
    name: str | None
    avatar_url: str | None
    oauth_accounts: list[OAuthAccount] = []

    class Settings:
        name = "users"
```

### Extending the User Model

Create your own model that extends the base:

```python
# src/app/models/user.py
from vibetuner.models import User as BaseUser
from pydantic import Field
class User(BaseUser):
bio: str | None = None
preferences: dict = Field(default_factory=dict)
class Settings:
name = "users"
```

## Session Management

Sessions use secure, HTTP-only cookies:

```python
# Default session configuration
SESSION_MAX_AGE = 60 * 60 * 24 * 30  # 30 days
SESSION_COOKIE_NAME = "session"
SESSION_SECRET_KEY = settings.SECRET_KEY
```

### Custom Session Configuration

Configure via environment variables in `.env`:

```bash
SESSION_MAX_AGE=604800  # 7 days in seconds
SESSION_COOKIE_SECURE=true  # HTTPS only
SESSION_COOKIE_SAMESITE=lax
```

## Protecting Routes

### Require Authentication

Use the `@require_auth` decorator:

```python
from vibetuner.frontend.auth import require_auth
@router.get("/dashboard")
@require_auth
async def dashboard(request: Request):
user = request.state.user
return templates.TemplateResponse("dashboard.html.jinja", {
"user": user
})
```

### Optional Authentication

Access user if authenticated, but don't require it:

```python
@router.get("/")
async def home(request: Request):
user = getattr(request.state, "user", None)
return templates.TemplateResponse("home.html.jinja", {
"user": user
})
```

### Template Context

User is automatically available in templates:

```html
{% if user %}
    <p>Welcome, {{ user.name }}!</p>
    <a href="/auth/logout">Logout</a>
{% else %}
    <a href="/auth/google">Sign in with Google</a>
    <a href="/auth/magic-link">Sign in with Email</a>
{% endif %}
```

## Custom Authentication Logic

### After Login Hook

Customize what happens after successful authentication:

```python
# src/app/frontend/hooks.py
async def on_user_login(user: User, request: Request):
# Log login event
# Update last_login timestamp
# Send welcome email
pass
```

Register in `src/app/frontend/__init__.py`:

```python
from vibetuner.frontend import events
from app.frontend.hooks import on_user_login
events.register("user_login", on_user_login)
```

## Security Considerations

### HTTPS in Production

Always use HTTPS in production:

```python
# Production settings
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_SAMESITE = "lax"  # CSRF protection
```

### Secret Key

Use a strong, unique secret key:

```bash
# Generate a secure key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Add to `.env`:

```bash
SECRET_KEY=your-generated-secret-key
```

### OAuth Callback URLs

Use exact URLs in OAuth provider settings:

```text
Development: http://localhost:8000/auth/google/callback
Production: https://example.com/auth/google/callback
```

### Rate Limiting

Consider adding rate limiting for authentication endpoints:

```python
from slowapi import Limiter
limiter = Limiter(key_func=lambda: request.client.host)
@router.post("/auth/magic-link")
@limiter.limit("5/minute")
async def request_magic_link(email: str):
# Send magic link
pass
```

## Troubleshooting

### OAuth Redirect Mismatch

Ensure callback URLs exactly match in:

1. OAuth provider settings
2. Your `.env` configuration
3. The URL used in production

### Magic Links Not Working

Check:

1. SMTP settings are correct
2. Email is being sent (check logs)
3. Token hasn't expired (15 minutes default)
4. Email isn't in spam folder

### Session Expires Too Quickly

Increase session duration:

```python
SESSION_MAX_AGE = 60 * 60 * 24 * 90  # 90 days
```

## Next Steps

- [Development Guide](development-guide.md) - Build features
- [Deployment](deployment.md) - Deploy to production
