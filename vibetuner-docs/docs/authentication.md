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
5. Add authorized redirect URI: `http://localhost:8000/auth/provider/google`
6. Enable in `tune.py`:

```python
# src/app/tune.py
from vibetuner import VibetunerApp

app = VibetunerApp(oauth_providers=["google"])
```

Add credentials to `.env`:

```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

### GitHub OAuth

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Create a new OAuth App
3. Set callback URL: `http://localhost:8000/auth/provider/github`
4. Enable in `tune.py`:

```python
# src/app/tune.py
from vibetuner import VibetunerApp

app = VibetunerApp(oauth_providers=["github"])
```

Add credentials to `.env`:

```bash
GITHUB_CLIENT_ID=your-client-id
GITHUB_CLIENT_SECRET=your-client-secret
```

You can enable multiple providers at once:

```python
app = VibetunerApp(oauth_providers=["google", "github"])
```

### Adding Custom OAuth Providers

Google and GitHub are built-in. Add any other OAuth provider using the
`custom_oauth_providers` dict in `tune.py`:

```python
# src/app/tune.py
from vibetuner import VibetunerApp
from vibetuner.models.oauth import OauthProviderModel

app = VibetunerApp(
    oauth_providers=["google"],  # built-in providers
    custom_oauth_providers={
        "twitter": OauthProviderModel(
            identifier="id",          # field in userinfo for unique ID
            params={
                "authorize_url": "https://twitter.com/i/oauth2/authorize",
                "access_token_url": "https://api.twitter.com/2/oauth2/token",
                "userinfo_endpoint": "https://api.twitter.com/2/users/me",
            },
            client_kwargs={"scope": "users.read tweet.read"},
            config={
                "TWITTER_CLIENT_ID": "your-client-id",
                "TWITTER_CLIENT_SECRET": "your-client-secret",
            },
        ),
    },
)
```

#### `OauthProviderModel` Fields

| Field | Type | Description |
|-------|------|-------------|
| `identifier` | `str` | Userinfo field that contains the unique user ID |
| `params` | `dict` | OAuth endpoint URLs (`authorize_url`, etc.) |
| `client_kwargs` | `dict` | Client settings (e.g., `{"scope": "..."}`) |
| `config` | `dict` | Credentials (`CLIENT_ID`, `CLIENT_SECRET`) |

The callback URL for any provider follows the pattern:
`/auth/provider/{provider_name}`

For more built-in providers, file an issue at
[github.com/alltuner/vibetuner](https://github.com/alltuner/vibetuner/issues).

### OAuth Account Linking

Vibetuner resolves returning users by their **OAuth account ID** (the
combination of `provider` + `provider_user_id`), not by email address.
This makes authentication resilient to email changes on the provider side.

The resolution flow works as follows:

1. **OAuth account exists** — User is found through the stored link between
   `OAuthAccountModel` and `UserModel`. Works even if the user's email has
   changed on the provider.
2. **OAuth account is new, email matches existing user** — The new OAuth
   account is linked to the existing user. This lets users sign in with
   multiple providers (e.g., Google and GitHub) and land on the same
   account.
3. **OAuth account is new, no matching email** — A new user account is
   created with the OAuth account linked.

This approach means:

- Users can change their email on Google/GitHub without losing access
- Multiple OAuth providers can be linked to one user account
- The `OAuthAccountModel` stores per-provider profile data (email, name,
  picture) separately from the main `UserModel`

## Magic Link Authentication

Magic links provide passwordless authentication via email.

### Configuration

Magic links are enabled by default. Configure email settings:

```bash
# .env
MAILJET_API_KEY=your-mailjet-api-key
MAILJET_API_SECRET=your-mailjet-api-secret
FROM_EMAIL=noreply@example.com
```

### How It Works

1. User enters email address
2. System sends email with unique token
3. User clicks link in email
4. System validates token and logs user in
5. Session created

### Customizing Email Templates

Edit `templates/email/magic_link.html.jinja`:

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
class UserModel(Document):
    email: str
    name: str | None
    picture: str | None

    class Settings:
        name = "users"
```

OAuth accounts are stored in a separate `OAuthAccountModel` collection
and linked to the user via `user_id`. See the
[Architecture](architecture.md) guide for the full schema.

### Extending the User Model

Create your own model that extends the base:

```python
# src/app/models/user.py
from vibetuner.models.user import UserModel
from pydantic import Field


class User(UserModel):
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
SESSION_SECRET_KEY = settings.SESSION_KEY
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
    return templates.TemplateResponse(
        "dashboard.html.jinja", {"user": user}
    )
```

### Optional Authentication

Access user if authenticated, but don't require it:

```python
@router.get("/")
async def home(request: Request):
    user = getattr(request.state, "user", None)
    return templates.TemplateResponse(
        "home.html.jinja", {"user": user}
    )
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
SESSION_KEY=your-generated-secret-key
```

### OAuth Callback URLs

Use exact URLs in OAuth provider settings:

```text
Development: http://localhost:8000/auth/provider/google
Production: https://example.com/auth/provider/google
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

1. Mailjet API credentials are correct
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
