# ABOUTME: Shared async Redis client for the vibetuner framework.
# ABOUTME: Provides a lazy-initialized, reusable Redis connection with graceful degradation.
import asyncio

from vibetuner.logging import logger


_client = None
_lock = asyncio.Lock()


async def get_redis_client():
    """Get or create the shared async Redis client.

    Returns None if ``redis_url`` is not configured. The client is lazily
    initialized on first call and reused across the application.
    """
    global _client
    if _client is not None:
        return _client

    from vibetuner.config import settings

    if settings.redis_url is None:
        return None

    async with _lock:
        if _client is not None:
            return _client

        import redis.asyncio as aioredis

        _client = aioredis.from_url(str(settings.redis_url))
        logger.debug("Shared Redis client initialized")
        return _client


async def close_redis_client() -> None:
    """Close the shared Redis client (call during application shutdown)."""
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None
        logger.debug("Shared Redis client closed")


def reset_redis_client() -> None:
    """Reset the client reference after a connection error.

    The next call to :func:`get_redis_client` will create a fresh connection.
    """
    global _client
    _client = None


def get_redis_url() -> str | None:
    """Return the configured Redis URL as a string, or None if not set.

    Useful for libraries (e.g. slowapi/limits) that accept a URI string
    rather than a client object.
    """
    from vibetuner.config import settings

    if settings.redis_url is None:
        return None
    return str(settings.redis_url)


def create_redis_client():
    """Create a new, independent async Redis client.

    Unlike :func:`get_redis_client`, each call returns a **separate** connection.
    Use this when a dedicated connection is needed (e.g. pub/sub).

    Returns None if ``redis_url`` is not configured.
    """
    from vibetuner.config import settings

    if settings.redis_url is None:
        return None

    import redis.asyncio as aioredis

    return aioredis.from_url(str(settings.redis_url))
