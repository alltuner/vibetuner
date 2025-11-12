# Models Module Development

Core database models for the vibetuner framework. This guide is for **developers working on the
framework**, not end users.

## Module Structure

```text
models/
├── user.py                 # User accounts and authentication
├── oauth.py                # OAuth provider accounts
├── email_verification.py   # Email verification tokens
├── blob.py                 # File storage metadata
└── mixins.py               # Reusable model behaviors
```

## Key Models

### UserModel (user.py)

The core user account model:

```python
class UserModel(Document, TimeStampMixin):
    email: EmailStr
    name: str | None
    oauth_accounts: list[Link[OAuthAccount]]
    # ... other fields
```

**Key features:**

- Email-based identification
- OAuth account linking (one-to-many)
- Created/updated timestamps via TimeStampMixin
- Indexed on email for fast lookup

**Used by:**

- Authentication system
- OAuth flows
- Magic link authentication
- User profile management

### OAuthAccount (oauth.py)

Links users to OAuth providers:

```python
class OAuthAccount(Document, TimeStampMixin):
    provider: str  # "google", "github", etc.
    provider_user_id: str
    user: Link[UserModel]
    # ... OAuth tokens and metadata
```

**Key features:**

- Stores OAuth tokens and refresh tokens
- Links to UserModel
- Indexed on (provider, provider_user_id)
- Handles account linking

### EmailVerificationToken (email_verification.py)

For magic link authentication:

```python
class EmailVerificationToken(Document):
    email: EmailStr
    token: str
    expires_at: datetime
```

**Key features:**

- Time-limited tokens
- Automatic cleanup of expired tokens
- One-time use (deleted after verification)

### Blob (blob.py)

File storage metadata:

```python
class Blob(Document, TimeStampMixin):
    key: str  # S3 key or local path
    content_type: str
    size: int
    uploaded_by: Link[UserModel] | None
```

**Key features:**

- Tracks uploaded files
- Links to uploader
- Storage backend agnostic (S3, local, etc.)

### TimeStampMixin (mixins.py)

Reusable timestamp behavior:

```python
class TimeStampMixin:
    db_insert_dt: datetime
    db_update_dt: datetime
```

Applied to most models for auditing.

## Development Guidelines

### Adding New Core Models

When adding models to the framework:

1. **Consider necessity**: Should this be in the framework or user code?
2. **Use mixins**: Apply TimeStampMixin if appropriate
3. **Add indexes**: Index frequently queried fields
4. **Link properly**: Use `Link[]` for relationships
5. **Register**: Models are auto-discovered from `models/__init__.py`

### Modifying Existing Models

When changing core models:

1. **Backward compatibility**: Consider existing data
2. **Migration path**: Provide migration script if needed
3. **Update indexes**: Modify `Settings.indexes` if needed
4. **Test with data**: Create test data and verify changes
5. **Document**: Update model docstrings

### Model Best Practices

**Indexing:**

```python
class MyModel(Document):
    field1: str
    field2: int

    class Settings:
        name = "my_collection"
        indexes = ["field1", ("field1", "field2")]
```

**Relationships:**

```python
# Use Link for references
owner: Link[UserModel]

# Use list[Link] for one-to-many
items: list[Link[Item]]
```

**Validation:**

```python
from pydantic import Field, validator

class MyModel(Document):
    email: EmailStr = Field(..., description="User email")

    @validator("email")
    def validate_email(cls, v):
        # Custom validation
        return v
```

## Testing

Test model changes:

```bash
# Scaffold test project
cd /Users/dpoblador/repos/vibetuner
uv run --directory vibetuner-py vibetuner scaffold new /tmp/test --defaults
cd /tmp/test

# Start services
just dev

# Test in Python
uv run python
>>> from vibetuner.models import UserModel, OAuthAccount
>>> # Test model operations
```

Test scenarios:

1. **Create**: Create instances and save
2. **Query**: Test find operations
3. **Update**: Modify and save
4. **Delete**: Remove instances
5. **Relationships**: Test Link resolution
6. **Indexes**: Verify index usage in queries

## Common Pitfalls

### Link Resolution

```python
# BAD: Doesn't resolve Link
user = await UserModel.get(user_id)
print(user.oauth_accounts)  # List of Link objects

# GOOD: Fetch links
user = await UserModel.get(user_id, fetch_links=True)
print(user.oauth_accounts)  # List of OAuthAccount objects
```

### Index Coverage

```python
# BAD: Query without index
await UserModel.find(MyModel.some_unindexed_field == "value").to_list()

# GOOD: Add index first
class MyModel(Document):
    some_field: str
    class Settings:
        indexes = ["some_field"]
```

### Migration Safety

When changing required fields:

```python
# BAD: Makes existing data invalid
class UserModel(Document):
    new_required_field: str  # Breaks existing users!

# GOOD: Make optional initially
class UserModel(Document):
    new_required_field: str | None = None  # Add migration to populate
```

## Related Files

- `vibetuner/mongo.py` - MongoDB connection setup
- `vibetuner/frontend/lifespan.py` - Model registration
- `vibetuner/frontend/deps.py` - User retrieval
