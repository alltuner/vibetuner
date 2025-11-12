# Frontend Module Development

This is the core frontend infrastructure for the vibetuner framework. This guide is for **developers
working on the framework**, not end users.

## Module Structure

```text
frontend/
├── routes/          # Default routes (auth, health, debug, lang, user, meta)
├── deps.py          # FastAPI dependencies (authentication, language, etc.)
├── middleware.py    # Request/response middleware
├── oauth.py         # OAuth provider integration
├── email.py         # Magic link email authentication
├── lifespan.py      # Application startup/shutdown lifecycle
├── context.py       # Request context management
├── hotreload.py     # Development hot-reload support
└── templates.py     # Template rendering utilities (moved to root)
```

## Key Components

### routes/

Default routes that every scaffolded project gets:

- **auth.py** - OAuth and magic link authentication flows
- **health.py** - Health check endpoints
- **debug.py** - Debug information (only in DEBUG mode)
- **lang.py** - Language selection
- **user.py** - User profile management
- **meta.py** - Metadata endpoints

Users extend these by creating routes in `src/app/frontend/routes/`.

### deps.py

FastAPI dependency injection functions:

- `get_current_user` - Require authentication (raises 403 if not authenticated)
- `get_current_user_optional` - Optional auth (returns None if not authenticated)
- `LangDep` - Current language from cookie/header
- `MagicCookieDep` - Magic link cookie for authentication

These are imported by user code for route protection.

### middleware.py

Request/response middleware:

- HTMX middleware (request/response helpers)
- Session middleware (secure cookie-based sessions)
- i18n middleware (internationalization)
- Context middleware (request context variables)

### oauth.py

OAuth provider integration using Authlib. Supports:

- Google OAuth
- GitHub OAuth
- Generic OAuth providers

Configuration via environment variables (CLIENT_ID, CLIENT_SECRET).

### email.py

Magic link authentication:

- Generate secure tokens
- Send magic link emails
- Validate and consume tokens
- Create/update user accounts

### lifespan.py

FastAPI lifespan management:

- MongoDB connection setup
- Redis connection (if background jobs enabled)
- Streaq worker initialization (if background jobs enabled)
- Model registration with Beanie

Users can extend via `src/app/frontend/lifespan.py` using `extend_lifespan` decorator.

### context.py

Request context management using contextvars. Provides:

- Current user context
- Request context
- Language context

Accessible throughout the request lifecycle without passing parameters.

### hotreload.py

Development hot-reload support. Watches:

- `src/app/` - User application code
- `templates/` - Template files

Triggers server reload on file changes in dev mode.

## Development Guidelines

### Adding New Routes

When adding new default routes:

1. Create route file in `routes/`
2. Register in `routes/__init__.py`
3. Test that it doesn't conflict with user routes
4. Document in user-facing AGENTS.md (in scaffolded projects)

### Modifying Dependencies

When changing FastAPI dependencies:

1. Ensure backward compatibility
2. Test with existing scaffolded projects
3. Update type hints
4. Document changes in CHANGELOG

### Middleware Changes

When modifying middleware:

1. Consider performance impact
2. Test with HTMX interactions
3. Verify session security
4. Test i18n functionality

### OAuth Provider Changes

When adding/modifying OAuth:

1. Test authentication flow end-to-end
2. Verify token handling
3. Test account linking
4. Document required environment variables

## Testing

Test changes by scaffolding a new project:

```bash
cd /Users/dpoblador/repos/vibetuner
uv run --directory vibetuner-py vibetuner scaffold new /tmp/test --defaults
cd /tmp/test
just dev
```

Test scenarios:

1. **Authentication**: OAuth login, magic link, logout
2. **Protected routes**: Access with/without auth
3. **HTMX**: Partial updates, form submissions
4. **Hot reload**: Code changes trigger reload
5. **i18n**: Language switching

## Common Pitfalls

### Session Security

- Always use secure cookies in production
- Set proper SameSite attributes
- Validate session tokens

### HTMX Middleware

- Don't break HTMX request/response headers
- Test partial updates
- Verify swap behaviors

### Context Management

- Use contextvars for request-scoped data
- Don't leak context between requests
- Clean up context properly

## Related Files

- `vibetuner/config.py` - Framework configuration
- `vibetuner/templates.py` - Template rendering (root level)
- `vibetuner/models/user.py` - User model
- `vibetuner/models/oauth.py` - OAuth account model
