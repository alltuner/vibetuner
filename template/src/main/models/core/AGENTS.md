# Core Models - DO NOT MODIFY

**⚠️ IMPORTANT**: Scaffolding-managed files. Changes will be lost on updates.

## Protected Files

- `user.py` - User authentication
- `oauth.py` - OAuth provider accounts
- `email_verification.py` - Magic link tokens
- `blob.py` - File storage metadata
- `mixins.py` - TimeStampMixin
- `types.py` - Shared types

## Extending Core Models

### Option 1: Composition

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

### Option 2: Related Models

```python
# models/user_profile.py
from beanie import Document
from pydantic import Field

class UserProfile(Document):
    user_id: str = Field(index=True)
    bio: str = ""
    avatar_url: str | None = None
```

## If Core Is Insufficient

1. Try composition or related models
2. Use service layer for business logic
3. Suggest enhancement to scaffolding repo
