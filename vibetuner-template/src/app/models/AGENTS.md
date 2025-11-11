# Application Models

**YOUR DATA MODELS GO HERE** - Define your MongoDB collections using Beanie ODM.

## What Goes Here

Create your application-specific data models in this directory:

- Blog posts, comments, articles
- Products, orders, inventory
- Projects, tasks, issues
- Any domain-specific entities

## Model Pattern

```python
# posts.py
from beanie import Document, Link
from pydantic import Field
from vibetuner.models import UserModel
from vibetuner.models.mixins import TimeStampMixin

class Post(Document, TimeStampMixin):
    """Blog post model."""

    title: str = Field(min_length=1, max_length=200)
    content: str
    author: Link[UserModel]
    tags: list[str] = []
    published: bool = False
    view_count: int = 0

    class Settings:
        name = "posts"  # Collection name in MongoDB
        indexes = [
            "author",
            "published",
            [("author", 1), ("published", -1)],  # Compound index
        ]
```

## Available from Core

### Core Models

Import these when you need to reference them:

```python
from vibetuner.models import (
    UserModel,              # User accounts
    OAuthAccountModel,      # OAuth provider links
    EmailVerificationTokenModel,  # Magic link tokens
    BlobModel,              # File storage
)
```

### Mixins

```python
from vibetuner.models.mixins import TimeStampMixin

# Provides:
# - db_insert_dt: datetime  # Auto-set on insert
# - db_update_dt: datetime  # Auto-updated on save
# - age() -> timedelta
# - age_in(unit: str) -> float
# - is_older_than(delta: timedelta) -> bool
```

### Field Types

```python
from vibetuner.models.types import (
    # Import any common types defined in core
)
```

## Common Patterns

### Linking to Users

```python
from beanie import Link
from vibetuner.models import UserModel

class UserProfile(Document):
    user: Link[UserModel]
    bio: str
    avatar_url: str | None = None
```

### Embedding Sub-documents

```python
from pydantic import BaseModel

class Address(BaseModel):
    street: str
    city: str
    country: str

class Customer(Document):
    name: str
    email: str
    addresses: list[Address] = []
```

### Soft Deletes

```python
class Post(Document, TimeStampMixin):
    title: str
    deleted_at: datetime | None = None

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    async def soft_delete(self) -> None:
        self.deleted_at = datetime.now(UTC)
        await self.save()
```

## Model Registration

Models are automatically discovered and registered if they:

1. Are in `src/app/models/`
2. Inherit from `Document`
3. Are imported in `src/app/models/__init__.py`

Update `__init__.py`:

```python
from beanie import Document, View

from .posts import Post
from .comments import Comment

APP_MODELS: list[type[Document] | type[View]] = [
    Post,
    Comment,
]
```

## Queries

### Basic Operations

```python
from beanie.operators import Eq, In, Gt, Lt

# Create
post = Post(title="Hello", content="World", author=user)
await post.insert()

# Find by ID
post = await Post.get(post_id)

# Find one by field
post = await Post.find_one(Eq(Post.title, "Hello"))

# Find many
posts = await Post.find(Eq(Post.published, True)).to_list()

# Update
post.view_count += 1
await post.save()

# Delete
await post.delete()
```

### Advanced Queries

```python
# Sorting and limiting
recent_posts = await Post.find(
    Eq(Post.published, True)
).sort(-Post.db_insert_dt).limit(10).to_list()

# Multiple conditions
popular_posts = await Post.find(
    Eq(Post.published, True),
    Gt(Post.view_count, 100)
).to_list()

# Text search (requires text index)
results = await Post.find(
    {"$text": {"$search": "python fastapi"}}
).to_list()

# Aggregation
from pymongo import DESCENDING

pipeline = [
    {"$match": {"published": True}},
    {"$group": {
        "_id": "$author",
        "post_count": {"$sum": 1}
    }},
    {"$sort": {"post_count": DESCENDING}}
]
results = await Post.aggregate(pipeline).to_list()
```

### Loading Relations

```python
# Fetch with linked documents
post = await Post.get(post_id, fetch_links=True)
print(post.author.email)  # Already loaded

# Without fetch_links
post = await Post.get(post_id)
await post.fetch_link(Post.author)  # Load explicitly
print(post.author.email)
```

## Indexes

```python
from pymongo import IndexModel, TEXT, ASCENDING, DESCENDING

class Post(Document):
    # ...

    class Settings:
        name = "posts"
        indexes = [
            "author",  # Simple index
            [("author", ASCENDING), ("published", DESCENDING)],  # Compound
            IndexModel([("title", TEXT), ("content", TEXT)]),  # Text search
            IndexModel(
                [("slug", ASCENDING)],
                unique=True,
                partialFilterExpression={"deleted_at": None}
            ),  # Unique with partial filter
        ]
```

## Validation

```python
from pydantic import Field, field_validator

class Post(Document):
    title: str = Field(min_length=1, max_length=200)
    slug: str = Field(pattern=r"^[a-z0-9-]+$")
    content: str = Field(min_length=10)

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        if v.startswith("-") or v.endswith("-"):
            raise ValueError("Slug cannot start or end with hyphen")
        return v
```

## Best Practices

1. **Use TimeStampMixin** - Track creation and modification times
2. **Define indexes** - Critical for query performance
3. **Type everything** - Leverage Pydantic's validation
4. **Use Links for relations** - Better than storing IDs manually
5. **Name collections explicitly** - Don't rely on defaults
6. **Consider soft deletes** - Safer than hard deletes
7. **Validate at model level** - Use Pydantic validators
8. **Document your models** - Add docstrings and field descriptions

## Testing Models

```python
import pytest
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

@pytest.fixture
async def db():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    await init_beanie(
        database=client.test_db,
        document_models=[Post]
    )
    yield
    await client.drop_database("test_db")

async def test_create_post(db):
    post = Post(title="Test", content="Content")
    await post.insert()
    assert post.id is not None
```

## MongoDB MCP

Claude Code has MongoDB MCP access for:

- Database inspection
- Query execution
- Index analysis
- Performance debugging

## Need Help?

- Core model changes: `https://github.com/alltuner/vibetuner`
- Beanie docs: `https://beanie-odm.dev/`
- MongoDB docs: `https://www.mongodb.com/docs/`
