# Optional Extras

Vibetuner uses optional dependency extras to keep production Docker images lean.
Install only what your project needs.

## Quick Reference

| Extra | What it provides | Key packages |
|-------|-----------------|--------------|
| `[all]` | Everything below | All packages |
| `[mongo]` | MongoDB / Beanie ODM | beanie, pymongo |
| `[auth]` | OAuth + user accounts | authlib (includes mongo) |
| `[s3]` | S3-compatible storage | aioboto3 |
| `[blobs]` | Blob storage with DB tracking | aioboto3, beanie (includes s3, mongo) |
| `[redis]` | Redis client | redis |
| `[worker]` | Background task queue | streaq (includes redis) |
| `[rate-limit-redis]` | Redis-backed rate limiting | redis |
| `[i18n]` | Internationalization | starlette-babel, babel |
| `[email]` | Email sending | mailjet-rest, resend |
| `[sql]` | SQL databases | sqlmodel |
| `[scaffold]` | Project scaffolding CLI | copier, gitpython |
| `[dev]` | Development tools | pytest, ruff, djlint, etc. |

## Installation

### Scaffolded projects (default)

Projects created with `vibetuner scaffold new` install `vibetuner[all]` by default.
No action needed unless you want to trim dependencies.

### Install specific extras

```bash
# MongoDB + auth + background jobs
uv add "vibetuner[mongo,auth,worker]"

# SQL database only
uv add "vibetuner[sql]"

# Everything
uv add "vibetuner[all]"
```

### Combine extras

Extras can be combined freely:

```bash
uv add "vibetuner[mongo,auth,redis,i18n,email]"
```

Some extras include others automatically:

- `[auth]` includes `[mongo]` (user accounts need a database)
- `[blobs]` includes `[s3]` and `[mongo]` (blob metadata stored in DB)
- `[worker]` includes `[redis]` (task queue needs Redis)

## Docker Image Optimization

The primary motivation for extras is smaller Docker images. A typical full install
is ~250MB of Python packages. With selective extras, an API-only service might need
only ~80MB.

### Example: Minimal API service

```dockerfile
# Only needs SQL, no auth/mongo/redis
RUN uv sync --frozen --no-dev --extra sql
```

### Example: Full web application

```dockerfile
# Everything except scaffold CLI (not needed at runtime)
RUN uv sync --frozen --no-dev --extra all
```

### Example: Background worker

```dockerfile
# Worker + mongo for models
RUN uv sync --frozen --no-dev --extra worker --extra mongo
```

## Graceful Degradation

When an extra is not installed, vibetuner degrades gracefully:

- **Missing `[auth]`**: No OAuth/login routes registered. Sessions still work.
- **Missing `[mongo]`**: No Beanie models loaded. SQL-only projects work fine.
- **Missing `[i18n]`**: English text shown as-is (no translation).
  `gettext_lazy` becomes a passthrough function.
- **Missing `[redis]`**: Rate limiting falls back to in-memory.
  Caching becomes a no-op.
- **Missing `[worker]`**: No background task queue available.
- **Missing `[email]`**: Email service raises a clear error when used.

### Startup Warnings

If your `tune.py` configures features that require missing extras, vibetuner
logs warnings at startup:

```text
WARNING: tune.py configures 'models' but [mongo] extra is not installed
WARNING: tune.py configures 'oauth_providers' but [auth] extra is not installed
```

## Checking Installed Extras

Use `vibetuner doctor` to see which extras are available:

```bash
uv run vibetuner doctor
```

Or check programmatically:

```python
from vibetuner.extras import has_extra

if has_extra("mongo"):
    from vibetuner.models import UserModel
```

## API Reference

The `vibetuner.extras` module provides three utilities:

```python
from vibetuner.extras import has_extra, require_extra, import_optional

# Check if an extra is installed (no side effects)
if has_extra("redis"):
    ...

# Raise ImportError with a helpful message if missing
require_extra("mongo", "CRUD route factory")

# Import a module, raising a clear error if the extra is missing
aioboto3 = import_optional("aioboto3", "s3", "S3 storage")
```
