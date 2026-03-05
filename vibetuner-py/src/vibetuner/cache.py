# ABOUTME: Response caching decorator backed by Redis.
# ABOUTME: Provides @cache for server-side route caching and invalidate() for cache busting.
import functools
import hashlib
import inspect
import json
from collections.abc import Callable
from typing import Any

from vibetuner.logging import logger


def _build_cache_key(prefix: str, path: str, query_params: str) -> str:
    """Build a deterministic Redis key from route path and query string."""
    raw = f"{path}?{query_params}" if query_params else path
    key_hash = hashlib.sha256(raw.encode()).hexdigest()[:16]
    return f"{prefix}cache:{key_hash}:{raw}"


def cache(
    expire: int = 60,
    *,
    force_caching: bool = False,
) -> Callable:
    """Decorator that caches route responses in Redis with a TTL.

    Cached responses are stored as JSON in Redis, keyed by route path and
    sorted query parameters.  When Redis is unavailable or not configured
    the decorator is a transparent no-op — the handler executes normally.

    In debug mode caching is **disabled by default** to avoid stale-data
    confusion during development.  Pass ``force_caching=True`` to override.

    Respects the ``Cache-Control: no-cache`` request header: when present
    the cache is bypassed and the response is regenerated (and re-stored).

    Args:
        expire: Time-to-live in seconds for the cached response.
        force_caching: Enable caching even when ``DEBUG`` is ``True``.

    Example::

        from vibetuner.cache import cache

        @router.get("/api/stats")
        @cache(expire=60)
        async def get_stats():
            return {"users": await count_users()}
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            from vibetuner.config import settings

            if settings.debug and not force_caching:
                return await _call_handler(func, *args, **kwargs)

            if settings.redis_url is None:
                return await _call_handler(func, *args, **kwargs)

            request = _extract_request(args, kwargs, func)
            if request is None:
                return await _call_handler(func, *args, **kwargs)

            return await _cached_call(func, args, kwargs, request, expire)

        return wrapper

    return decorator


async def _cached_call(
    func: Callable,
    args: tuple,
    kwargs: dict,
    request: Any,
    expire: int,
) -> Any:
    """Execute the handler with Redis caching, falling back on errors."""
    from vibetuner.config import settings
    from vibetuner.redis import get_redis_client, reset_redis_client

    no_cache = request.headers.get("cache-control", "") == "no-cache"
    sorted_qs = "&".join(f"{k}={v}" for k, v in sorted(request.query_params.items()))
    cache_key = _build_cache_key(settings.redis_key_prefix, request.url.path, sorted_qs)

    try:
        client = await get_redis_client()
        if client is None:
            return await _call_handler(func, *args, **kwargs)

        if not no_cache:
            cached = await client.get(cache_key)
            if cached is not None:
                return _restore_response(cached)

        response = await _call_handler(func, *args, **kwargs)

        serialized = _serialize_response(response)
        if serialized is not None:
            await client.set(cache_key, serialized, ex=expire)

        return response

    except (ConnectionError, OSError, TimeoutError):
        logger.debug("Redis cache unavailable, executing handler directly")
        reset_redis_client()
        return await _call_handler(func, *args, **kwargs)
    except Exception:
        logger.debug("Redis cache error, executing handler directly")
        return await _call_handler(func, *args, **kwargs)


async def invalidate(path: str, *, query_params: str = "") -> bool:
    """Remove a cached response by route path.

    Args:
        path: The URL path to invalidate (e.g. ``"/api/stats"``).
        query_params: Optional sorted query string to target a specific variant.

    Returns:
        ``True`` if a cached entry was deleted, ``False`` otherwise.
    """
    try:
        from vibetuner.config import settings
        from vibetuner.redis import get_redis_client

        client = await get_redis_client()
        if client is None:
            return False

        cache_key = _build_cache_key(settings.redis_key_prefix, path, query_params)
        deleted = await client.delete(cache_key)
        return deleted > 0
    except (ConnectionError, OSError, TimeoutError):
        logger.debug("Redis unavailable during cache invalidation")
        return False
    except Exception:
        logger.debug("Cache invalidation failed")
        return False


async def invalidate_pattern(pattern: str) -> int:
    """Remove all cached responses matching a key pattern.

    Uses Redis ``SCAN`` to find matching keys without blocking.

    Args:
        pattern: Glob pattern relative to the cache namespace
            (e.g. ``"/api/*"``).

    Returns:
        Number of keys deleted.
    """
    try:
        from vibetuner.config import settings
        from vibetuner.redis import get_redis_client

        client = await get_redis_client()
        if client is None:
            return 0

        full_pattern = f"{settings.redis_key_prefix}cache:*:{pattern}"
        deleted = 0
        async for key in client.scan_iter(match=full_pattern, count=100):
            await client.delete(key)
            deleted += 1
        return deleted
    except (ConnectionError, OSError, TimeoutError):
        logger.debug("Redis unavailable during pattern invalidation")
        return 0
    except Exception:
        logger.debug("Pattern invalidation failed")
        return 0


# ── Internal helpers ────────────────────────────────────────────────


async def _call_handler(func: Callable, *args: Any, **kwargs: Any) -> Any:
    """Call the route handler, supporting both sync and async functions."""
    if inspect.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    return func(*args, **kwargs)


def _extract_request(args: tuple, kwargs: dict, func: Callable):
    """Find the Request object from route arguments."""
    # Check kwargs first (FastAPI typically passes as keyword)
    from starlette.requests import Request

    for v in kwargs.values():
        if isinstance(v, Request):
            return v
    for v in args:
        if isinstance(v, Request):
            return v
    return None


def _serialize_response(response: Any) -> bytes | None:
    """Serialize a response for Redis storage."""
    from starlette.responses import HTMLResponse, JSONResponse, Response

    if isinstance(response, JSONResponse):
        return json.dumps(
            {
                "type": "json",
                "body": response.body.decode(),
                "status": response.status_code,
            }
        ).encode()

    if isinstance(response, HTMLResponse):
        return json.dumps(
            {
                "type": "html",
                "body": response.body.decode(),
                "status": response.status_code,
            }
        ).encode()

    if isinstance(response, Response) and hasattr(response, "body"):
        content_type = response.headers.get("content-type", "")
        return json.dumps(
            {
                "type": "response",
                "body": response.body.decode(),
                "status": response.status_code,
                "content_type": content_type,
            }
        ).encode()

    # Dict responses (FastAPI auto-serializes these)
    if isinstance(response, dict):
        return json.dumps(
            {
                "type": "dict",
                "body": json.dumps(response),
            }
        ).encode()

    return None


def _restore_response(cached: bytes) -> Any:
    """Deserialize a cached response back into a Starlette response or dict."""
    from starlette.responses import HTMLResponse, Response

    data = json.loads(cached)
    resp_type = data["type"]

    if resp_type == "json":
        return Response(
            content=data["body"],
            status_code=data.get("status", 200),
            media_type="application/json",
        )

    if resp_type == "html":
        return HTMLResponse(
            content=data["body"],
            status_code=data.get("status", 200),
        )

    if resp_type == "response":
        return Response(
            content=data["body"],
            status_code=data.get("status", 200),
            media_type=data.get("content_type", "text/plain"),
        )

    if resp_type == "dict":
        return json.loads(data["body"])

    return Response(content=data.get("body", ""), status_code=200)
