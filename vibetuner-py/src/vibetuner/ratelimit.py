# ABOUTME: Rate limiting support for vibetuner routes using slowapi.
# ABOUTME: Auto-configures with vibetuner's Redis connection and provides a clean decorator API.
from slowapi import Limiter
from slowapi.middleware import SlowAPIASGIMiddleware
from slowapi.util import get_remote_address

from vibetuner.config import settings
from vibetuner.logging import logger
from vibetuner.redis import get_redis_url


def _build_limiter() -> Limiter:
    storage_uri = get_redis_url()

    kwargs: dict = {
        "key_func": get_remote_address,
        "enabled": settings.rate_limit.enabled,
        "headers_enabled": settings.rate_limit.headers_enabled,
        "key_prefix": f"{settings.redis_key_prefix}ratelimit:",
        "strategy": settings.rate_limit.strategy,
        "swallow_errors": settings.rate_limit.swallow_errors,
        "config_filename": None,
    }

    if storage_uri:
        kwargs["storage_uri"] = storage_uri
        kwargs["in_memory_fallback_enabled"] = True
        logger.debug("Rate limiter using Redis storage: {}", storage_uri)
    else:
        kwargs["storage_uri"] = "memory://"
        logger.debug("Rate limiter using in-memory storage (no Redis configured)")

    default_limits = settings.rate_limit.default_limits
    if default_limits:
        kwargs["default_limits"] = default_limits

    return Limiter(**kwargs)


limiter: Limiter = _build_limiter()

__all__ = ["limiter", "SlowAPIASGIMiddleware"]
