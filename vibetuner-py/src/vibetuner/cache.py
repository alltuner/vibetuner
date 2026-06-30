# ABOUTME: Response caching decorator backed by Redis.
# ABOUTME: Provides @cache for server-side route caching and invalidate() for cache busting.
import fnmatch
import functools
import hashlib
import inspect
import json
from collections.abc import Callable
from typing import Any

from vibetuner.logging import logger


_GLOB_CHARS = frozenset("*?[")


def _build_cache_key(
    prefix: str, path: str, query_params: str, vary_value: str | None = None
) -> str:
    """Build a deterministic Redis key from route path, query string, and vary value."""
    raw = f"{path}?{query_params}" if query_params else path
    if vary_value:
        raw = f"{raw}|vary:{vary_value}"
    key_hash = hashlib.sha256(raw.encode()).hexdigest()[:16]
    return f"{prefix}cache:{key_hash}:{raw}"


def _registry_key(prefix: str, path: str) -> str:
    """Redis SET holding every cache key written for a route path."""
    return f"{prefix}cache-index:{path}"


def _paths_key(prefix: str) -> str:
    """Redis SET holding every route path with a key registry."""
    return f"{prefix}cache-paths"


def _as_str(value: bytes | str) -> str:
    return value.decode() if isinstance(value, bytes) else value


def cache(
    expire: int = 60,
    *,
    force_caching: bool = False,
    vary_on: Callable | None = None,
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
        vary_on: Optional callable ``(Request) -> str`` that returns an
            additional cache key component derived from the request. Use
            this to produce per-user, per-tenant, or per-locale cache
            entries. The return value is appended to the cache key, so
            different values yield independent cached responses.

            When ``None`` (the default), the cache key is based solely on
            the request path and query parameters.

    Example::

        from vibetuner.cache import cache

        @router.get("/api/stats")
        @cache(expire=60)
        async def get_stats():
            return {"users": await count_users()}

        # Per-user caching (each user gets their own cached copy)
        @router.get("/dashboard")
        @cache(expire=120, vary_on=lambda r: str(r.state.user.id))
        async def dashboard(request: Request):
            return await render_dashboard(request)

        # Per-tenant caching
        @router.get("/reports")
        @cache(expire=300, vary_on=lambda r: r.state.tenant_id)
        async def reports(request: Request):
            return await generate_reports(request)
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

            return await _cached_call(func, args, kwargs, request, expire, vary_on)

        return wrapper

    return decorator


async def _cached_call(
    func: Callable,
    args: tuple,
    kwargs: dict,
    request: Any,
    expire: int,
    vary_on: Callable | None = None,
) -> Any:
    """Execute the handler with Redis caching, falling back on errors."""
    from vibetuner.config import settings
    from vibetuner.redis import get_redis_client, reset_redis_client

    no_cache = request.headers.get("cache-control", "") == "no-cache"
    sorted_qs = "&".join(f"{k}={v}" for k, v in sorted(request.query_params.items()))
    vary_value = vary_on(request) if vary_on is not None else None
    cache_key = _build_cache_key(
        settings.redis_key_prefix, request.url.path, sorted_qs, vary_value
    )

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
            await _register_cache_key(
                client, settings.redis_key_prefix, request.url.path, cache_key, expire
            )

        return response

    except (ConnectionError, OSError, TimeoutError):
        logger.debug("Redis cache unavailable, executing handler directly")
        reset_redis_client()
        return await _call_handler(func, *args, **kwargs)
    except Exception:
        logger.debug("Redis cache error, executing handler directly")
        return await _call_handler(func, *args, **kwargs)


async def invalidate(
    path: str, *, query_params: str = "", vary: str | None = None
) -> bool:
    """Remove a cached response by route path.

    Args:
        path: The URL path to invalidate (e.g. ``"/api/stats"``).
        query_params: Optional sorted query string to target a specific variant.
        vary: Optional vary value to target the entry written for a route
            cached with ``vary_on`` (e.g. the user id returned by the
            ``vary_on`` callable). Without it, only the non-vary'd entry
            for the path can be hit.

    Returns:
        ``True`` if a cached entry was deleted, ``False`` otherwise.
    """
    try:
        from vibetuner.config import settings
        from vibetuner.redis import get_redis_client

        client = await get_redis_client()
        if client is None:
            return False

        cache_key = _build_cache_key(
            settings.redis_key_prefix, path, query_params, vary
        )
        deleted = await client.delete(cache_key)
        return deleted > 0
    except (ConnectionError, OSError, TimeoutError):
        logger.debug("Redis unavailable during cache invalidation")
        return False
    except Exception:
        logger.debug("Cache invalidation failed")
        return False


async def invalidate_pattern(pattern: str) -> int:
    """Remove cached responses for a route path or glob pattern.

    Works off the per-path key registries maintained at cache-write time,
    so cost is proportional to the number of cached variants — never a
    full-keyspace ``SCAN``. A full keyspace scan against a large or remote
    Redis can block for minutes and must never run in the request path;
    this function intentionally has no such fallback.

    A bare path (no ``*``, ``?``, or ``[`` glob characters) removes **every**
    cached variant of that path: all query-string and ``vary_on`` variants,
    plus the registry itself. A glob pattern is matched against the raw
    ``path?query|vary:value`` portion of each registered key.

    Only entries written through ``@cache`` are registered; anything else
    is untouched and expires via its own TTL.

    Args:
        pattern: Route path or glob pattern relative to the cache namespace
            (e.g. ``"/dashboard"`` or ``"/api/*"``).

    Returns:
        Number of cache entries deleted.
    """
    try:
        from vibetuner.config import settings
        from vibetuner.redis import get_redis_client

        client = await get_redis_client()
        if client is None:
            return 0

        prefix = settings.redis_key_prefix
        if not _GLOB_CHARS & set(pattern):
            return await _invalidate_path(client, prefix, pattern)

        full_pattern = f"{prefix}cache:*:{pattern}"
        paths = [_as_str(p) for p in await client.smembers(_paths_key(prefix))]
        deleted = 0
        for path in paths:
            registry = _registry_key(prefix, path)
            keys = [_as_str(m) for m in await client.smembers(registry)]
            matching = [k for k in keys if fnmatch.fnmatchcase(k, full_pattern)]
            if not matching:
                continue
            deleted += await client.unlink(*matching)
            if len(matching) == len(keys):
                await client.unlink(registry)
                await client.srem(_paths_key(prefix), path)
            else:
                await client.srem(registry, *matching)
        return deleted
    except (ConnectionError, OSError, TimeoutError):
        logger.debug("Redis unavailable during pattern invalidation")
        return 0
    except Exception:
        logger.debug("Pattern invalidation failed")
        return 0


async def _invalidate_path(client: Any, prefix: str, path: str) -> int:
    """Delete every registered cache entry for a path plus its registry."""
    registry = _registry_key(prefix, path)
    keys = [_as_str(m) for m in await client.smembers(registry)]
    deleted = await client.unlink(*keys) if keys else 0
    await client.unlink(registry)
    await client.srem(_paths_key(prefix), path)
    return deleted


# ── Internal helpers ────────────────────────────────────────────────


async def _register_cache_key(
    client: Any, prefix: str, path: str, cache_key: str, expire: int
) -> None:
    """Record a written cache key in the per-path registry sets.

    The registry set and the path index get their TTL bumped to at least
    ``expire`` (``EXPIRE NX`` seeds a TTL, ``EXPIRE GT`` only ever extends
    it), so a registry always outlives the longest-lived entry it tracks
    and expired-entry bookkeeping cannot accumulate forever.

    Failures are swallowed: the response is already cached and registry
    bookkeeping must not affect the request.
    """
    try:
        registry = _registry_key(prefix, path)
        paths = _paths_key(prefix)
        pipe = client.pipeline(transaction=False)
        pipe.sadd(registry, cache_key)
        pipe.expire(registry, expire, nx=True)
        pipe.expire(registry, expire, gt=True)
        pipe.sadd(paths, path)
        pipe.expire(paths, expire, nx=True)
        pipe.expire(paths, expire, gt=True)
        await pipe.execute()
    except Exception:
        logger.debug("Cache key registry update failed")


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
