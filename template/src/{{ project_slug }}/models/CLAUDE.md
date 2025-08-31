# Models Module

MongoDB data models using Beanie ODM.

## Structure

**Add your models here:**

- Create files directly in `models/` (e.g., `posts.py`, `products.py`)

**Core models (DO NOT MODIFY):**

- `core/user.py` - User authentication
- `core/oauth.py` - OAuth provider accounts
- `core/email_verification.py` - Magic link tokens
- `core/mixins.py` - Reusable model components
- `core/blob.py` - File storage models

## Model Pattern

```python
from beanie import Document
from pydantic import Field
from .core.mixins import TimeStampMixin

class Product(Document, TimeStampMixin):
    name: str
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    
    class Settings:
        name = "products"
        indexes = ["name"]
```

## Mixins

Use `TimeStampMixin` for automatic timestamps:

- `db_insert_dt` - Set on creation (UTC)
- `db_update_dt` - Updated on save (UTC)

## Queries

```python
# Find operations
product = await Product.find_one(Product.name == "Widget")
products = await Product.find(Product.price < 100).to_list()

# Save operations
await product.save()
await product.replace()
await product.delete()

# Aggregation
pipeline = [{"$match": {"price": {"$gt": 50}}}]
results = await Product.aggregate(pipeline).to_list()
```

## Indexes

Define in model's `Settings` class:

```python
class Settings:
    indexes = [
        "field_name",
        [("field1", 1), ("field2", -1)],  # Compound index
        IndexModel([("text_field", TEXT)])  # Text index
    ]
```

## Relationships

Use `Link` for document references:

```python
from beanie import Link

class Order(Document):
    user: Link[User]
    products: list[Link[Product]]
```

## MongoDB MCP Integration

Claude Code has access to the **MongoDB MCP server** for database operations:

- Query collections directly
- Inspect document structures
- Run aggregation pipelines
- Debug database issues
- Explore data relationships

This is automatically connected to your project's MongoDB instance (`{{ project_slug }}` database).
