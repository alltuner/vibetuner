# Core Models - DO NOT MODIFY

**⚠️ IMPORTANT**: These files are managed by the scaffolding system and should NEVER be modified directly.

## Why These Files Are Protected

- Maintained by the scaffolding template
- Updates come through `just update-scaffolding`
- Manual changes will be lost on scaffolding updates
- Breaking changes here can corrupt authentication/user management

## If You Need Changes

### Option 1: Extend via Custom Models

Create your own models that extend or complement core models:

```python
# models/extended_user.py
from .core.user import User as BaseUser

class ExtendedUser(BaseUser):
    # Add your custom fields
    bio: str = ""
    preferences: dict = {}
```

### Option 2: Request Scaffolding Update

If a core feature is missing:

1. **Document the need**: What feature/change is required?
2. **Suggest to user**: "This requires a scaffolding update. Consider:
   - Filing an issue in the scaffolding repository
   - Forking and customizing the scaffolding template
   - Implementing a workaround in your custom code"
3. **Backport changes**: If critical, suggest the user contributes the change back to the scaffolding template

## Core Model Files

- `user.py` - User authentication and profile
- `oauth.py` - OAuth provider accounts
- `email_verification.py` - Magic link tokens
- `blob.py` - File storage metadata
- `mixins.py` - Reusable model components (TimeStampMixin)
- `types.py` - Shared type definitions

## Available Mixins

### TimeStampMixin

- Adds automatic `db_insert_dt` and `db_update_dt` timestamps
- Provides age calculation methods: `age()`, `age_in()`, `is_older_than()`

## How to Work Around Limitations

Instead of modifying core models:

1. **Use composition**: Create related models that reference core models
2. **Use service layer**: Add business logic in `services/` directory
3. **Use middleware**: Intercept and enhance at the request level
4. **Use database views**: Create MongoDB aggregation pipelines

## Example: Adding User Preferences

❌ **WRONG** - Modifying core/user.py:

```python
# DON'T DO THIS in core/user.py
class User(Document):
    preferences: dict = {}  # Will be lost on update!
```

✅ **CORRECT** - Creating a separate model:

```python
# models/user_preferences.py
from beanie import Document, Link
from .core.user import User

class UserPreferences(Document):
    user: Link[User]
    theme: str = "light"
    notifications: bool = True
    
    class Settings:
        name = "user_preferences"
```

## Getting Help

If you're blocked by core model limitations:

1. Check if there's a workaround pattern above
2. Suggest filing an issue in the scaffolding repo
3. Consider if the feature belongs in application code instead
