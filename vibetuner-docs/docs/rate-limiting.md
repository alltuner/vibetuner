# Rate Limiting

Protect your routes from abuse with built-in rate limiting, powered by
[slowapi](https://github.com/laurents/slowapi) and backed by Redis.

<!-- markdownlint-disable MD046 -->

!!! note "Package name convention"
    In all examples, `app` refers to your project's Python package (the directory
    under `src/`). The actual name depends on your project slug (e.g.,
    `src/myproject/` for a project named "myproject").

## Overview

Rate limiting is enabled by default and works out of the box. When Redis is
configured, limits are shared across workers with automatic in-memory fallback
if Redis becomes unavailable. Without Redis, limits use in-memory storage
(per-process, suitable for development).

## Quick Start

### Per-Route Limits

Apply rate limits to individual routes with the `@limiter.limit()` decorator:

```python
# src/app/frontend/routes/api.py
from fastapi import APIRouter, Request
from vibetuner.ratelimit import limiter

router = APIRouter()

@router.get("/api/search")
@limiter.limit("10/minute")
async def search(request: Request):
    return {"results": []}

@router.post("/api/submit")
@limiter.limit("5/minute")
async def submit(request: Request):
    return {"status": "ok"}
```

!!! warning "Request parameter required"
    Every rate-limited route **must** have a `request: Request` parameter.
    slowapi uses it to identify the client. Routes without it will raise
    an error at startup.

### Global Default Limits

Set default limits that apply to all routes via environment variables:

```bash
# .env
RATE_LIMIT_DEFAULT_LIMITS='["100/hour", "10/second"]'
```

Routes with explicit `@limiter.limit()` decorators override the defaults.

### Exempt Routes

Exclude routes from rate limiting (useful for health checks or public assets):

```python
from vibetuner.ratelimit import limiter

@router.get("/health")
@limiter.exempt
async def health(request: Request):
    return {"status": "ok"}
```

## How It Works

### Client Identification

By default, clients are identified by their IP address (from `X-Forwarded-For`
header when behind a proxy, or the direct client IP). This works for most use
cases.

### Rate Limit Strings

Limits follow the format `"X per Y"` or `"X/Y"`:

| Format | Meaning |
|---|---|
| `"10/second"` | 10 requests per second |
| `"30/minute"` | 30 requests per minute |
| `"100/hour"` | 100 requests per hour |
| `"1000/day"` | 1000 requests per day |
| `"5 per minute"` | 5 requests per minute |

Multiple limits can be combined on a single route:

```python
@router.get("/api/data")
@limiter.limit("2/second")
@limiter.limit("100/hour")
async def get_data(request: Request):
    ...
```

### Response Headers

When `RATE_LIMIT_HEADERS_ENABLED=true` (default), responses include standard
rate limit headers:

| Header | Description |
|---|---|
| `X-RateLimit-Limit` | Maximum requests allowed in the window |
| `X-RateLimit-Remaining` | Requests remaining in the current window |
| `X-RateLimit-Reset` | Seconds until the window resets |
| `Retry-After` | Seconds to wait before retrying (on 429 responses) |

### 429 Response

When a client exceeds the limit, a `429 Too Many Requests` JSON response is
returned:

```json
{"error": "Rate limit exceeded: 10 per 1 minute"}
```

## Configuration

All settings are configurable via environment variables with the `RATE_LIMIT_`
prefix:

| Variable | Default | Description |
|---|---|---|
| `RATE_LIMIT_ENABLED` | `true` | Enable/disable rate limiting globally |
| `RATE_LIMIT_DEFAULT_LIMITS` | `[]` | Default limits for all routes (JSON list) |
| `RATE_LIMIT_HEADERS_ENABLED` | `true` | Include `X-RateLimit-*` response headers |
| `RATE_LIMIT_STRATEGY` | `fixed-window` | Rate limiting strategy |
| `RATE_LIMIT_SWALLOW_ERRORS` | `true` | Swallow storage errors instead of crashing |

### Strategies

| Strategy | Description |
|---|---|
| `fixed-window` | Simple fixed time windows (default, lowest overhead) |
| `moving-window` | Sliding window for smoother rate limiting |
| `sliding-window-counter` | Approximation between fixed and moving window |

### Storage

- **With Redis** (`REDIS_URL` set): Limits are stored in Redis, shared across
  all workers. If Redis becomes unavailable, automatically falls back to
  in-memory storage.
- **Without Redis**: Limits use in-memory storage (per-process). Suitable for
  development but not for production with multiple workers.

## Advanced Usage

### Custom Key Functions

Rate limit by something other than IP address (e.g., authenticated user):

```python
from fastapi import Request
from vibetuner.ratelimit import limiter

def key_by_user(request: Request) -> str:
    if request.user.is_authenticated:
        return str(request.user.identity)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host if request.client else "127.0.0.1"

@router.get("/api/premium")
@limiter.limit("1000/hour", key_func=key_by_user)
async def premium_endpoint(request: Request):
    ...
```

### Shared Limits

Apply the same limit across multiple routes:

```python
from vibetuner.ratelimit import limiter

shared_api_limit = limiter.shared_limit("100/hour", scope="api")

@router.get("/api/users")
@shared_api_limit
async def list_users(request: Request):
    ...

@router.get("/api/posts")
@shared_api_limit
async def list_posts(request: Request):
    ...
```

### Conditional Exemption

Exempt certain requests dynamically:

```python
@router.get("/api/data")
@limiter.limit(
    "10/minute",
    exempt_when=lambda: request.user.is_authenticated,
)
async def get_data(request: Request):
    ...
```

### Dynamic Limits

Use a callable to determine the limit at runtime:

```python
def get_limit_for_user(request: Request) -> str:
    if request.user.is_authenticated:
        return "100/minute"
    return "10/minute"

@router.get("/api/search")
@limiter.limit(get_limit_for_user)
async def search(request: Request):
    ...
```

## Disabling Rate Limiting

### Globally

```bash
RATE_LIMIT_ENABLED=false
```

### For Development

Rate limiting is enabled even in development mode. To disable it locally:

```bash
# .env.local
RATE_LIMIT_ENABLED=false
```

## Troubleshooting

### Rate Limits Not Shared Across Workers

Ensure `REDIS_URL` is set. Without Redis, each worker process tracks limits
independently.

### "No request argument" Error

Every rate-limited route must accept a `request: Request` parameter:

```python
# GOOD
@router.get("/api/data")
@limiter.limit("10/minute")
async def get_data(request: Request):
    ...

# BAD - will raise an error
@router.get("/api/data")
@limiter.limit("10/minute")
async def get_data():
    ...
```

### Limits Not Applying

1. Check that `RATE_LIMIT_ENABLED` is not set to `false`
2. Verify the decorator order — `@limiter.limit()` should come after
   `@router.get()`:

    ```python
    @router.get("/endpoint")   # First: route decorator
    @limiter.limit("10/minute")  # Second: rate limit
    async def endpoint(request: Request):
        ...
    ```

3. Run `vibetuner doctor` to verify Redis connectivity

## Next Steps

- [Background Tasks](background-tasks.md) — Redis-backed task queue
- [Authentication](authentication.md) — Protect routes with auth
- [Deployment](deployment.md) — Production configuration
