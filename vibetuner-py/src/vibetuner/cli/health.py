# ABOUTME: Lightweight worker healthcheck for container probes.
# ABOUTME: Looks up streaq health keys by worker id; skips the full CLI/app bootstrap.
import asyncio
from typing import TYPE_CHECKING

from vibetuner.logging import logger


if TYPE_CHECKING:
    from redis.asyncio import Redis


# streaq names its default-priority stream, consumer group and per-worker health
# keys this way. Every worker reads that stream as a consumer named after its id.
_STREAM = "streaq:{queue}:queues:normal"
_GROUP = "workers"
_HEALTH_KEY = "streaq:{queue}:health:{worker_id}"


async def has_live_worker(client: "Redis", queue_name: str) -> bool:
    """Return whether any worker on ``queue_name`` has a fresh health key.

    The worker ids come from the stream's consumer group, so the lookup costs
    two round trips no matter how many unrelated keys the Redis holds. streaq
    never removes consumers, so ids of stopped workers stay listed; their health
    keys have expired and they don't count.
    """
    from redis.exceptions import ResponseError

    try:
        consumers = await client.xinfo_consumers(
            _STREAM.format(queue=queue_name), _GROUP
        )
    except ResponseError as exc:
        # No worker has started on this queue yet: no stream or no group.
        if "NOGROUP" in str(exc) or "no such key" in str(exc):
            return False
        raise
    if not consumers:
        return False

    async with client.pipeline(transaction=False) as pipe:
        for consumer in consumers:
            worker_id = consumer["name"]
            if isinstance(worker_id, bytes):
                worker_id = worker_id.decode()
            pipe.exists(_HEALTH_KEY.format(queue=queue_name, worker_id=worker_id))
        results: list[int] = await pipe.execute()
    return any(results)


async def library_promotes_delayed_tasks(redis_url: str, prefix: str) -> bool:
    """Probe the streaq Lua library this Redis server has installed.

    Opens its own coredis client, since streaq's Lua wrappers are coredis
    commands while the rest of this probe speaks redis-py.
    """
    import coredis

    from vibetuner.tasks.lua_library import promotes_delayed_tasks

    async with coredis.Redis.from_url(
        redis_url, decode_responses=True, connect_timeout=3, stream_timeout=3
    ) as client:
        return await promotes_delayed_tasks(client, prefix)


async def check_worker() -> int:
    """Return 0 if a live worker can actually run delayed work, 1 otherwise.

    The streaq worker renews a health key in Redis from inside its event loop,
    so a wedged loop lets the key expire. A live worker is still useless when
    another project's streaq has replaced the server-global Lua library, so
    this also checks that a due task really is promoted. Both checks import
    only the config and Redis clients, keeping the probe well under a container
    healthcheck timeout.
    """
    from vibetuner.config import settings

    if not settings.workers_available:
        logger.error("worker-health: REDIS_URL not configured")
        return 1

    import redis.asyncio as aioredis

    queue_name = settings.redis_key_prefix.rstrip(":")
    client = aioredis.from_url(
        str(settings.redis_url), socket_timeout=3, socket_connect_timeout=3
    )
    try:
        found = await has_live_worker(client, queue_name)
    except Exception as exc:  # noqa: BLE001
        logger.error("worker-health: Redis check failed: {}", exc)
        return 1
    finally:
        await client.aclose()

    if not found:
        logger.error("worker-health: no live worker found for queue {}", queue_name)
        return 1

    try:
        promotes = await library_promotes_delayed_tasks(
            str(settings.redis_url), settings.redis_key_prefix
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("worker-health: Lua library check failed: {}", exc)
        return 1

    if not promotes:
        logger.error(
            "worker-health: streaq's versioned Lua library on this Redis server "
            "does not promote delayed tasks, so no delayed or cron task runs. "
            "Another project sharing this Redis server loaded the same versioned "
            "library from an incompatible streaq release, or no worker has loaded "
            "it yet. A separate database number does not isolate Redis functions."
        )
        return 1
    return 0


def run() -> None:
    """Console fast-path entry: run the check and exit with its status."""
    raise SystemExit(asyncio.run(check_worker()))
