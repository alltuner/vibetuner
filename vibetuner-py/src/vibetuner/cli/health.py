# ABOUTME: Lightweight worker healthcheck for container probes.
# ABOUTME: Reads only the streaq health key; skips the full CLI/app bootstrap.
import asyncio

from vibetuner.logging import logger


async def check_worker() -> int:
    """Return 0 if a live worker is found, 1 otherwise.

    The streaq worker renews a health key in Redis from inside its event loop,
    so a wedged loop lets the key expire. This checks for a fresh key while
    importing only the config and Redis client, keeping the probe well under a
    container healthcheck timeout.
    """
    from vibetuner.config import settings

    if not settings.workers_available:
        logger.error("worker-health: REDIS_URL not configured")
        return 1

    import redis.asyncio as aioredis

    queue_name = settings.redis_key_prefix.rstrip(":")
    pattern = f"streaq:{queue_name}:health:*"
    client = aioredis.from_url(
        str(settings.redis_url), socket_timeout=3, socket_connect_timeout=3
    )
    found = False
    try:
        async for _key in client.scan_iter(match=pattern, count=100):
            found = True
            break
    except Exception as exc:
        logger.error("worker-health: Redis check failed: {}", exc)
        return 1
    finally:
        await client.aclose()

    if not found:
        logger.error("worker-health: no live worker found for queue {}", queue_name)
        return 1
    return 0


def run() -> None:
    """Console fast-path entry: run the check and exit with its status."""
    raise SystemExit(asyncio.run(check_worker()))
