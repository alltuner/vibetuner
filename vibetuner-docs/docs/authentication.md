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
            scopes=["users.read", "tweet.read"],
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
| `scopes` | `list[str]` | OAuth scopes to request (default `[]`) |
| `client_kwargs` | `dict` | Extra client settings (e.g., `token_endpoint_auth_method`) |
| `config` | `dict` | Credentials (`CLIENT_ID`, `CLIENT_SECRET`) |
| `compliance_fix` | `Callable \| None` | Authlib compliance fix callback (default `None`) |
| `login_routes` | `bool` | Create login/callback routes (default `True`) |

The callback URL for any provider follows the pattern:
`/auth/provider/{provider_name}`

#### Providers Without Login Routes

Some apps need OAuth providers for **account linking** (e.g., connecting a
LinkedIn profile to publish on its behalf), not for user login. Set
`login_routes=False` to register a provider for credential management only,
without creating the default login/callback routes:

```python
app = VibetunerApp(
    custom_oauth_providers={
        "linkedin": OauthProviderModel(
            identifier="sub",
            params={...},
            scopes=["openid", "profile", "email"],
            config={...},
            login_routes=False,  # no /auth/login/provider/linkedin route
        ),
    },
)
```

The provider is still available for `resolve_oauth_client()` and
database-backed OAuth apps. Your app can define its own callback routes
for custom flows like account linking.

#### Compliance Fixes

Some OAuth providers deviate from the spec in ways that break standard token
handling. Authlib supports `compliance_fix` callbacks to patch these responses
before they are parsed. Pass one via the `compliance_fix` field:

```python
from vibetuner.models.oauth import OauthProviderModel


def strip_id_token(session, token):
    """LinkedIn includes an id_token that triggers OIDC nonce validation failure."""
    token.pop("id_token", None)
    return token


app = VibetunerApp(
    custom_oauth_providers={
        "linkedin": OauthProviderModel(
            identifier="sub",
            params={
                "authorize_url": "https://www.linkedin.com/oauth/v2/authorization",
                "access_token_url": "https://www.linkedin.com/oauth/v2/accessToken",
                "userinfo_endpoint": "https://api.linkedin.com/v2/userinfo",
            },
            scopes=["openid", "profile", "email"],
            config={
                "LINKEDIN_CLIENT_ID": "your-client-id",
                "LINKEDIN_CLIENT_SECRET": "your-client-secret",
            },
            compliance_fix=strip_id_token,
        ),
    },
)
```

The fix is automatically applied to both env-var-based and database-backed OAuth
apps that use the same provider.

For more built-in providers, file an issue at
[github.com/alltuner/vibetuner](https://github.com/alltuner/vibetuner/issues).

### Database-Backed OAuth Apps

`OAuthProviderAppModel` stores OAuth credentials (`client_id`, `client_secret`,
scopes, metadata) in MongoDB with optional encryption at rest. It supports two
usage patterns:

1. **Authlib-integrated login**: Register a provider via `oauth_providers` in
   `tune.py`, then use `resolve_oauth_client()` for redirect-based login flows.
   The model inherits endpoints and compliance fixes from the registered
   `OauthProviderModel`.
2. **Credentials store**: Use the model purely to store and retrieve
   `client_id`/`client_secret` for platforms with non-standard auth flows
   (e.g., Meta Graph API long-lived token exchange, Spotify client credentials
   grant, YouTube Data API). Query credentials via `get_active_by_provider()`
   without involving Authlib at all.

Both patterns benefit from encrypted secret storage and the `is_active` flag
for credential rotation.

#### Creating an OAuth App

```python
from vibetuner.models.oauth_app import OAuthProviderAppModel

app = OAuthProviderAppModel(
    provider="linkedin",       # must match a registered provider name
    name="Acme Corp",
    client_id="app-specific-client-id",
    client_secret="app-specific-secret",
    scopes=["openid", "profile", "email", "w_member_social"],
    metadata={"org_id": "12345"},
)
await app.insert()
```

#### `OAuthProviderAppModel` Fields

| Field | Type | Description |
|-------|------|-------------|
| `provider` | `str` | Registered provider name (e.g., `"google"`) |
| `name` | `str` | Human-readable label |
| `client_id` | `str` | OAuth client ID for this app |
| `client_secret` | `str` | OAuth client secret for this app |
| `external_app_id` | `str \| None` | Provider's own identifier for this app |
| `scopes` | `list[str]` | Scope overrides (empty = use provider defaults) |
| `capabilities` | `list[str]` | Detected capabilities for this app |
| `is_active` | `bool` | Whether available for use (default `True`) |
| `metadata` | `dict` | Provider-specific extra data |

#### Resolving OAuth Clients

Use `resolve_oauth_client` to resolve the correct Authlib client for a given
provider, with optional app-specific credentials:

```python
from vibetuner.frontend.oauth import resolve_oauth_client

# Environment-variable credentials (default)
client_name = await resolve_oauth_client("google", app_id=None)

# Database-backed app credentials
client_name = await resolve_oauth_client("linkedin", app_id="6801...")
```

When `app_id` is `None`, the function returns the bare provider name (using
env-var credentials). When an `app_id` is provided, it loads the
`OAuthProviderAppModel` from the database, registers a namespaced Authlib
client with the app's credentials, and returns the client name.

The built-in login and callback routes accept an optional `app_id` query
parameter that flows through this resolution automatically.

#### Login Page

Active database-backed OAuth apps appear on the login page as additional
sign-in buttons alongside env-var providers. Each button shows the
provider name and the app's human-readable `name` field (e.g.,
"Continue with Google · Acme Corp").

Only apps whose `provider` references a registered provider with
`login_routes=True` are displayed. Inactive apps (`is_active=False`)
are excluded. No extra configuration is needed; creating an active
`OAuthProviderAppModel` for a registered provider is enough.

The provider must be registered via env-var credentials for its login
route to exist. Database-backed apps for a provider that has no
env-var registration will not appear on the login page because the
route they would link to does not exist.

#### App-to-Account Linking

When a user authenticates through a database-backed OAuth app, the `app_id`
is stored on the `OAuthAccountModel`. This lets you trace which app was
used for each OAuth account link.

#### Using as a Credentials Store

Not every platform uses standard redirect-based OAuth. For platforms like
Meta Graph API (Instagram, Threads, Facebook), YouTube Data API, or Spotify
(client credentials grant), you can use `OAuthProviderAppModel` purely as an
encrypted credentials store, without registering the provider in Authlib.

```python
from vibetuner.models.oauth_app import OAuthProviderAppModel

# Store credentials for a non-Authlib platform
app = OAuthProviderAppModel(
    provider="instagram",
    name="My Instagram App",
    client_id="ig-client-id",
    client_secret="ig-client-secret",
    metadata={"app_type": "business"},
)
await app.insert()
```

Retrieve credentials at runtime with `get_active_by_provider()`:

```python
from vibetuner.models.oauth_app import OAuthProviderAppModel

apps = await OAuthProviderAppModel.get_active_by_provider("instagram")
for app in apps:
    # app.client_id and app.client_secret are available as plaintext
    # (decrypted automatically if FIELD_ENCRYPTION_KEY is set)
    client = SomeExternalSDK(
        client_id=app.client_id,
        client_secret=app.client_secret,
    )
```

This pattern gives you the same benefits as the Authlib-integrated path
(encrypted storage, `is_active` toggling, per-app metadata) without forcing
the platform into a redirect-based flow.

The `provider` field is a free-form string in this context. It does not need
to match a registered `OauthProviderModel`; it only needs to be consistent
so `get_active_by_provider()` returns the right credentials.

### Encrypting OAuth Secrets at Rest

Database-backed OAuth app secrets (`client_secret`) are stored as plaintext by
default. You can encrypt them at rest using a passphrase-derived Fernet key.

#### Setting the Encryption Key

```bash
# Generate a key automatically and encrypt all existing secrets
vibetuner crypto set-key

# Or provide your own passphrase
vibetuner crypto set-key --key "my-secure-passphrase"
```

This will:

1. Encrypt all plaintext `client_secret` values in MongoDB
2. Write `FIELD_ENCRYPTION_KEY` to your `.env` file

#### How It Works

Once `FIELD_ENCRYPTION_KEY` is set in your environment:

- **On save**: `client_secret` is Fernet-encrypted before writing to MongoDB
- **On load**: `client_secret` is transparently decrypted when reading from
  MongoDB

Your application code works with plaintext secrets as usual. Encryption is
handled automatically by the model layer.

#### Key Rotation

```bash
# Rotate to a new auto-generated key
vibetuner crypto rotate-key

# Or specify the new key
vibetuner crypto rotate-key --new-key "new-secure-passphrase"
```

Rotation re-encrypts all secrets with the new key in a single operation
and updates your `.env` file.

#### Behavior Without a Key

When `FIELD_ENCRYPTION_KEY` is not set:

- Secrets are stored and read as plaintext (no encryption)
- Existing plaintext secrets continue to work normally
- If an encrypted value is encountered without a key, an error is raised

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
# Option A: Resend (recommended)
MAIL_RESEND_API_KEY=re_xxxxxxxxxxxx

# Option B: Mailjet
# MAIL_MAILJET_API_KEY=your-api-key
# MAIL_MAILJET_API_SECRET=your-api-secret

# Option C: Cloudflare Email Service (public beta)
# MAIL_CLOUDFLARE_API_TOKEN=cf-token
# MAIL_CLOUDFLARE_ACCOUNT_ID=your-account-id

FROM_EMAIL=noreply@example.com
```

When multiple providers are configured, auto-detection prefers Resend, then
Mailjet, then Cloudflare. Set `MAIL_PROVIDER=cloudflare` (or `resend` /
`mailjet`) to pick explicitly.

### Resend rate limits and quota

Resend caps sends at 5 requests/second per team and enforces a monthly quota.
When a send exceeds either limit, Resend returns HTTP 429 and the provider
raises a `RateLimitError` — the send fails loudly rather than silently, so a
burst of magic-link requests can surface errors. The framework does **not**
retry or queue these; handle bursts upstream (for example, by sending mail from
a background task) if you expect to approach 5 req/s.

On every send the provider logs Resend's `ratelimit-*` and
`x-resend-monthly-quota` response headers at `DEBUG`, and logs a `WARNING` with
those headers when a `RateLimitError` is raised. Raise the log level to `DEBUG`
to watch your remaining per-second budget and monthly usage.

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

These templates are rendered by the framework's static-render engine, which
**auto-escapes context variables for HTML and XML templates** (`.html.jinja`,
`.xml.jinja`). Plain-text templates (`.txt.jinja`) are emitted verbatim. So any
user-derived value (display name, profile field) is safely escaped in the HTML
email without action on your part. If you need to inject pre-rendered, trusted
markup, opt out explicitly with Jinja's `| safe` filter.

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
    <form method="post" action="/auth/logout">
        <button type="submit">Logout</button>
    </form>
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

### Session Key

Sessions are signed with `SESSION_KEY`. Generate a strong, unique value and
add it to your `.env`:

```bash
uv run vibetuner crypto generate-key
```

```bash
SESSION_KEY=your-generated-secret-key
```

The framework ships a placeholder `SESSION_KEY` so a fresh project runs
without configuration. Startup **fails closed** when this placeholder is still
in place and `ENVIRONMENT=prod`, so you can never sign production sessions
with a publicly known key. Outside production it only logs a loud warning.

### OAuth Callback URLs

Use exact URLs in OAuth provider settings:

```text
Development: http://localhost:8000/auth/provider/google
Production: https://example.com/auth/provider/google
```

### Logout is POST-only

`/auth/logout` only signs the user out via `POST`. A `GET` to the same path
renders a confirmation interstitial with a small form that submits the POST.

This prevents drive-by logout attacks where a cross-origin page embeds the
old URL (`<img src="https://example.com/auth/logout">`) and silently ends
the visitor's session. Use a form, not a link, in your own templates:

```html
<form method="post" action="/auth/logout">
    <button type="submit">Log out</button>
</form>
```

### Rate Limiting

The magic-link send and OAuth-initiation endpoints carry a conservative
per-IP rate limit out of the box (default `5/minute`) to curb email flooding
and account enumeration. Tune it via `RATE_LIMIT_AUTH_LIMITS`:

```bash
# .env
RATE_LIMIT_AUTH_LIMITS=10/minute
```

See [Rate Limiting](rate-limiting.md) for the full configuration surface and
how to apply limits to your own routes.

### Safe Redirects

Post-login redirect targets (the `next` query/form value and the language
switcher's `current`) are validated before use. Only same-origin relative
paths are honored; absolute (`https://evil.com`) and protocol-relative
(`//evil.com`) values fall back to the homepage, preventing open redirects.

## Troubleshooting

### OAuth Redirect Mismatch

Ensure callback URLs exactly match in:

1. OAuth provider settings
2. Your `.env` configuration
3. The URL used in production

### Magic Links Not Working

Check:

1. Email provider credentials are correct (MAIL_RESEND_API_KEY, MAIL_MAILJET_API_KEY, or MAIL_CLOUDFLARE_API_TOKEN + MAIL_CLOUDFLARE_ACCOUNT_ID)
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
