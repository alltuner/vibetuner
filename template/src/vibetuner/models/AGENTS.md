# Core Models Module

**IMMUTABLE SCAFFOLDING CODE** - These are the framework's core models that provide essential functionality.

## What's Here

This module contains the scaffolding's core models:

- **UserModel** - Base user model with authentication support
- **OAuthAccountModel** - OAuth provider account linking
- **EmailVerificationTokenModel** - Magic link authentication tokens
- **BlobModel** - File storage and blob management
- **Mixins** - Reusable model behaviors (TimeStampMixin, etc.)
- **Types** - Common field types and validators

## Important Rules

⚠️  **DO NOT MODIFY** these core models directly.

**For changes to core models:**

- File an issue at `https://github.com/alltuner/scaffolding`
- Core changes benefit all projects using the scaffolding

**For your application models:**

- Create them in `src/app/models/` instead
- Import core models when needed: `from vibetuner.models import UserModel`
- Use mixins from here: `from vibetuner.models.mixins import TimeStampMixin`

## User Model Pattern (for reference)

Your application models in `src/app/models/` should follow this pattern:

```python
from beanie import Document
from pydantic import Field
from vibetuner.models.mixins import TimeStampMixin

class Product(Document, TimeStampMixin):
    name: str
    price: float = Field(gt=0)
    stock: int = Field(ge=0)

    class Settings:
        name = "products"
        indexes = ["name"]
```

## Available Mixins

### TimeStampMixin

Automatic timestamps for all models:

- `db_insert_dt` - Created at (UTC)
- `db_update_dt` - Updated at (UTC)
- Methods: `age()`, `age_in()`, `is_older_than()`

Import in your app models:

```python
from vibetuner.models.mixins import TimeStampMixin
```

## Queries

### Finding Documents

```python
from beanie.operators import Eq, In, Gt, Lt

# By ID (preferred method)
product = await Product.get(product_id)

# By field (use Beanie operators)
product = await Product.find_one(Eq(Product.name, "Widget"))
products = await Product.find(Lt(Product.price, 100)).to_list()

# Multiple conditions
results = await Product.find(
    Eq(Product.category, "electronics"),
    Gt(Product.price, 50)
).to_list()

# With In operator
products = await Product.find(
    In(Product.category, ["electronics", "gadgets"])
).to_list()
```

### Save/Delete

```python
# Create
product = Product(name="Widget", price=9.99, stock=100)
await product.insert()

# Update
product.price = 19.99
await product.save()

# Delete
await product.delete()
```

### Aggregation

```python
results = await Product.aggregate([
    {"$match": {"price": {"$gt": 50}}},
    {"$group": {"_id": "$category", "total": {"$sum": 1}}}
]).to_list()
```

## Indexes

```python
from pymongo import IndexModel, TEXT

class Settings:
    indexes = [
        "field_name",  # Simple index
        [("field1", 1), ("field2", -1)],  # Compound index
        IndexModel([("text_field", TEXT)])  # Text search
    ]
```

## Relationships

```python
from beanie import Link

class Order(Document):
    user: Link[User]
    products: list[Link[Product]]

# Fetch with relations
order = await Order.get(order_id, fetch_links=True)
print(order.user.email)  # Automatically loaded
```

## Extending Core Models

If you need to add fields to User or other core models:

1. **Option A**: File an issue at `https://github.com/alltuner/scaffolding` for widely useful fields
2. **Option B**: Create a related model in `src/app/models/` that links to the core model:

```python
from beanie import Document, Link
from vibetuner.models import UserModel

class UserProfile(Document):
    user: Link[UserModel]
    bio: str
    avatar_url: str

    class Settings:
        name = "user_profiles"
```

## MongoDB MCP

Claude Code has MongoDB MCP access for database operations, queries, and debugging.
