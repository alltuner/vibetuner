# ABOUTME: Redis client wrapper that applies project/environment namespace prefixing
# ABOUTME: Ensures all Redis keys are isolated by project and environment

from __future__ import annotations

from builtins import set as _set
from typing import Any

from redis.asyncio import Redis


class NamespacedRedis:
    """Redis client wrapper that automatically prefixes all keys with project namespace.

    All keys are prefixed with "{project_slug}:{env}:" for dev or "{project_slug}:" for prod.
    This ensures Redis key isolation when multiple projects or environments share the same
    Redis instance.
    """

    def __init__(self, redis: Redis, prefix: str) -> None:
        self._redis = redis
        self._prefix = prefix

    def _prefixed(self, key: str) -> str:
        return f"{self._prefix}{key}"

    def _prefixed_keys(self, keys: list[str]) -> list[str]:
        return [self._prefixed(k) for k in keys]

    # String operations

    async def get(self, key: str) -> Any:
        return await self._redis.get(self._prefixed(key))

    async def set(
        self,
        key: str,
        value: Any,
        ex: int | None = None,
        px: int | None = None,
        nx: bool = False,
        xx: bool = False,
    ) -> Any:
        return await self._redis.set(
            self._prefixed(key), value, ex=ex, px=px, nx=nx, xx=xx
        )

    async def setex(self, key: str, seconds: int, value: Any) -> Any:
        return await self._redis.setex(self._prefixed(key), seconds, value)

    async def setnx(self, key: str, value: Any) -> bool:
        return await self._redis.setnx(self._prefixed(key), value)

    async def delete(self, *keys: str) -> int:
        return await self._redis.delete(*self._prefixed_keys(list(keys)))

    async def exists(self, *keys: str) -> int:
        return await self._redis.exists(*self._prefixed_keys(list(keys)))

    async def expire(self, key: str, seconds: int) -> bool:
        return await self._redis.expire(self._prefixed(key), seconds)

    async def ttl(self, key: str) -> int:
        return await self._redis.ttl(self._prefixed(key))

    async def incr(self, key: str) -> int:
        return await self._redis.incr(self._prefixed(key))

    async def decr(self, key: str) -> int:
        return await self._redis.decr(self._prefixed(key))

    async def incrby(self, key: str, amount: int) -> int:
        return await self._redis.incrby(self._prefixed(key), amount)

    # Hash operations

    async def hget(self, name: str, key: str) -> Any:
        return await self._redis.hget(self._prefixed(name), key)

    async def hset(
        self,
        name: str,
        key: str | None = None,
        value: Any = None,
        mapping: dict[str, Any] | None = None,
    ) -> int:
        return await self._redis.hset(
            self._prefixed(name), key=key, value=value, mapping=mapping
        )

    async def hgetall(self, name: str) -> dict[str, Any]:
        return await self._redis.hgetall(self._prefixed(name))

    async def hdel(self, name: str, *keys: str) -> int:
        return await self._redis.hdel(self._prefixed(name), *keys)

    async def hexists(self, name: str, key: str) -> bool:
        return await self._redis.hexists(self._prefixed(name), key)

    async def hincrby(self, name: str, key: str, amount: int = 1) -> int:
        return await self._redis.hincrby(self._prefixed(name), key, amount)

    # List operations

    async def lpush(self, name: str, *values: Any) -> int:
        return await self._redis.lpush(self._prefixed(name), *values)

    async def rpush(self, name: str, *values: Any) -> int:
        return await self._redis.rpush(self._prefixed(name), *values)

    async def lpop(self, name: str, count: int | None = None) -> Any:
        return await self._redis.lpop(self._prefixed(name), count)

    async def rpop(self, name: str, count: int | None = None) -> Any:
        return await self._redis.rpop(self._prefixed(name), count)

    async def lrange(self, name: str, start: int, end: int) -> list[Any]:
        return await self._redis.lrange(self._prefixed(name), start, end)

    async def llen(self, name: str) -> int:
        return await self._redis.llen(self._prefixed(name))

    # Set operations

    async def sadd(self, name: str, *values: Any) -> int:
        return await self._redis.sadd(self._prefixed(name), *values)

    async def srem(self, name: str, *values: Any) -> int:
        return await self._redis.srem(self._prefixed(name), *values)

    async def smembers(self, name: str) -> _set[Any]:
        return await self._redis.smembers(self._prefixed(name))

    async def sismember(self, name: str, value: Any) -> bool:
        return await self._redis.sismember(self._prefixed(name), value)

    async def scard(self, name: str) -> int:
        return await self._redis.scard(self._prefixed(name))

    async def sdiff(self, *keys: str) -> _set[Any]:
        return await self._redis.sdiff(*self._prefixed_keys(list(keys)))

    async def sdiffstore(self, dest: str, *keys: str) -> int:
        return await self._redis.sdiffstore(
            self._prefixed(dest), *self._prefixed_keys(list(keys))
        )

    # Sorted set operations

    async def zadd(
        self, name: str, mapping: dict[str, float], nx: bool = False, xx: bool = False
    ) -> int:
        return await self._redis.zadd(self._prefixed(name), mapping, nx=nx, xx=xx)

    async def zrem(self, name: str, *values: Any) -> int:
        return await self._redis.zrem(self._prefixed(name), *values)

    async def zrange(
        self, name: str, start: int, end: int, withscores: bool = False
    ) -> list[Any]:
        return await self._redis.zrange(
            self._prefixed(name), start, end, withscores=withscores
        )

    async def zrangebyscore(
        self,
        name: str,
        min_score: float,
        max_score: float,
        withscores: bool = False,
    ) -> list[Any]:
        return await self._redis.zrangebyscore(
            self._prefixed(name), min_score, max_score, withscores=withscores
        )

    async def zscore(self, name: str, value: Any) -> float | None:
        return await self._redis.zscore(self._prefixed(name), value)

    async def zcard(self, name: str) -> int:
        return await self._redis.zcard(self._prefixed(name))

    # Key pattern operations (prefix is applied to pattern)

    async def keys(self, pattern: str = "*") -> list[str]:
        prefixed_pattern = self._prefixed(pattern)
        keys = await self._redis.keys(prefixed_pattern)
        prefix_len = len(self._prefix)
        return [
            k[prefix_len:] if isinstance(k, str) else k.decode()[prefix_len:]
            for k in keys
        ]

    # Pipeline support

    def pipeline(self, transaction: bool = True) -> "NamespacedPipeline":
        return NamespacedPipeline(self._redis.pipeline(transaction), self._prefix)

    # Access to underlying client for advanced operations

    @property
    def raw(self) -> Redis:
        """Access the underlying Redis client for operations not covered by this wrapper."""
        return self._redis

    @property
    def prefix(self) -> str:
        """The prefix applied to all keys."""
        return self._prefix


class NamespacedPipeline:
    """Pipeline wrapper that applies namespace prefix to all operations."""

    def __init__(self, pipeline: Any, prefix: str) -> None:
        self._pipeline = pipeline
        self._prefix = prefix

    def _prefixed(self, key: str) -> str:
        return f"{self._prefix}{key}"

    async def execute(self) -> list[Any]:
        return await self._pipeline.execute()

    # String operations

    def get(self, key: str) -> "NamespacedPipeline":
        self._pipeline.get(self._prefixed(key))
        return self

    def set(
        self,
        key: str,
        value: Any,
        ex: int | None = None,
        px: int | None = None,
    ) -> "NamespacedPipeline":
        self._pipeline.set(self._prefixed(key), value, ex=ex, px=px)
        return self

    def delete(self, *keys: str) -> "NamespacedPipeline":
        for key in keys:
            self._pipeline.delete(self._prefixed(key))
        return self

    def incr(self, key: str) -> "NamespacedPipeline":
        self._pipeline.incr(self._prefixed(key))
        return self

    def expire(self, key: str, seconds: int) -> "NamespacedPipeline":
        self._pipeline.expire(self._prefixed(key), seconds)
        return self

    # Hash operations

    def hset(
        self,
        name: str,
        key: str | None = None,
        value: Any = None,
        mapping: dict[str, Any] | None = None,
    ) -> "NamespacedPipeline":
        self._pipeline.hset(self._prefixed(name), key=key, value=value, mapping=mapping)
        return self

    def hget(self, name: str, key: str) -> "NamespacedPipeline":
        self._pipeline.hget(self._prefixed(name), key)
        return self

    def hgetall(self, name: str) -> "NamespacedPipeline":
        self._pipeline.hgetall(self._prefixed(name))
        return self

    # List operations

    def lpush(self, name: str, *values: Any) -> "NamespacedPipeline":
        self._pipeline.lpush(self._prefixed(name), *values)
        return self

    def rpush(self, name: str, *values: Any) -> "NamespacedPipeline":
        self._pipeline.rpush(self._prefixed(name), *values)
        return self

    # Set operations

    def sadd(self, name: str, *values: Any) -> "NamespacedPipeline":
        self._pipeline.sadd(self._prefixed(name), *values)
        return self

    def smembers(self, name: str) -> "NamespacedPipeline":
        self._pipeline.smembers(self._prefixed(name))
        return self

    # Sorted set operations

    def zadd(self, name: str, mapping: dict[str, float]) -> "NamespacedPipeline":
        self._pipeline.zadd(self._prefixed(name), mapping)
        return self

    def zrange(
        self, name: str, start: int, end: int, withscores: bool = False
    ) -> "NamespacedPipeline":
        self._pipeline.zrange(self._prefixed(name), start, end, withscores=withscores)
        return self


async def create_namespaced_redis(redis_url: str, prefix: str) -> NamespacedRedis:
    """Create a namespaced Redis client.

    Args:
        redis_url: Redis connection URL
        prefix: Key prefix (typically from settings.redis_key_prefix)

    Returns:
        NamespacedRedis client with automatic key prefixing
    """
    redis = Redis.from_url(redis_url, decode_responses=True)
    return NamespacedRedis(redis, prefix)
