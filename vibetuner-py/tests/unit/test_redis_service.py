# ABOUTME: Unit tests for vibetuner.services.redis module
# ABOUTME: Tests NamespacedRedis key prefixing functionality
# ruff: noqa: S101

from unittest.mock import AsyncMock, MagicMock

import pytest
from vibetuner.services.redis import NamespacedPipeline, NamespacedRedis


@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
    redis = AsyncMock()
    redis.pipeline = MagicMock(return_value=AsyncMock())
    return redis


@pytest.fixture
def namespaced_redis(mock_redis):
    """Create a NamespacedRedis instance with a test prefix."""
    return NamespacedRedis(mock_redis, "testproject:dev:")


class TestNamespacedRedisStringOperations:
    """Test string operations with namespace prefixing."""

    @pytest.mark.asyncio
    async def test_get_prefixes_key(self, namespaced_redis, mock_redis):
        """Test that get() prefixes the key."""
        await namespaced_redis.get("mykey")
        mock_redis.get.assert_called_once_with("testproject:dev:mykey")

    @pytest.mark.asyncio
    async def test_set_prefixes_key(self, namespaced_redis, mock_redis):
        """Test that set() prefixes the key."""
        await namespaced_redis.set("mykey", "myvalue", ex=60)
        mock_redis.set.assert_called_once_with(
            "testproject:dev:mykey", "myvalue", ex=60, px=None, nx=False, xx=False
        )

    @pytest.mark.asyncio
    async def test_setex_prefixes_key(self, namespaced_redis, mock_redis):
        """Test that setex() prefixes the key."""
        await namespaced_redis.setex("mykey", 3600, "myvalue")
        mock_redis.setex.assert_called_once_with(
            "testproject:dev:mykey", 3600, "myvalue"
        )

    @pytest.mark.asyncio
    async def test_delete_prefixes_keys(self, namespaced_redis, mock_redis):
        """Test that delete() prefixes all keys."""
        await namespaced_redis.delete("key1", "key2", "key3")
        mock_redis.delete.assert_called_once_with(
            "testproject:dev:key1", "testproject:dev:key2", "testproject:dev:key3"
        )

    @pytest.mark.asyncio
    async def test_exists_prefixes_keys(self, namespaced_redis, mock_redis):
        """Test that exists() prefixes all keys."""
        await namespaced_redis.exists("key1", "key2")
        mock_redis.exists.assert_called_once_with(
            "testproject:dev:key1", "testproject:dev:key2"
        )

    @pytest.mark.asyncio
    async def test_incr_prefixes_key(self, namespaced_redis, mock_redis):
        """Test that incr() prefixes the key."""
        await namespaced_redis.incr("counter")
        mock_redis.incr.assert_called_once_with("testproject:dev:counter")


class TestNamespacedRedisHashOperations:
    """Test hash operations with namespace prefixing."""

    @pytest.mark.asyncio
    async def test_hget_prefixes_name(self, namespaced_redis, mock_redis):
        """Test that hget() prefixes the hash name."""
        await namespaced_redis.hget("myhash", "field")
        mock_redis.hget.assert_called_once_with("testproject:dev:myhash", "field")

    @pytest.mark.asyncio
    async def test_hset_prefixes_name(self, namespaced_redis, mock_redis):
        """Test that hset() prefixes the hash name."""
        await namespaced_redis.hset("myhash", key="field", value="value")
        mock_redis.hset.assert_called_once_with(
            "testproject:dev:myhash", key="field", value="value", mapping=None
        )

    @pytest.mark.asyncio
    async def test_hgetall_prefixes_name(self, namespaced_redis, mock_redis):
        """Test that hgetall() prefixes the hash name."""
        await namespaced_redis.hgetall("myhash")
        mock_redis.hgetall.assert_called_once_with("testproject:dev:myhash")


class TestNamespacedRedisListOperations:
    """Test list operations with namespace prefixing."""

    @pytest.mark.asyncio
    async def test_lpush_prefixes_name(self, namespaced_redis, mock_redis):
        """Test that lpush() prefixes the list name."""
        await namespaced_redis.lpush("mylist", "value1", "value2")
        mock_redis.lpush.assert_called_once_with(
            "testproject:dev:mylist", "value1", "value2"
        )

    @pytest.mark.asyncio
    async def test_rpush_prefixes_name(self, namespaced_redis, mock_redis):
        """Test that rpush() prefixes the list name."""
        await namespaced_redis.rpush("mylist", "value1")
        mock_redis.rpush.assert_called_once_with("testproject:dev:mylist", "value1")

    @pytest.mark.asyncio
    async def test_lrange_prefixes_name(self, namespaced_redis, mock_redis):
        """Test that lrange() prefixes the list name."""
        await namespaced_redis.lrange("mylist", 0, -1)
        mock_redis.lrange.assert_called_once_with("testproject:dev:mylist", 0, -1)


class TestNamespacedRedisSetOperations:
    """Test set operations with namespace prefixing."""

    @pytest.mark.asyncio
    async def test_sadd_prefixes_name(self, namespaced_redis, mock_redis):
        """Test that sadd() prefixes the set name."""
        await namespaced_redis.sadd("myset", "value1", "value2")
        mock_redis.sadd.assert_called_once_with(
            "testproject:dev:myset", "value1", "value2"
        )

    @pytest.mark.asyncio
    async def test_smembers_prefixes_name(self, namespaced_redis, mock_redis):
        """Test that smembers() prefixes the set name."""
        await namespaced_redis.smembers("myset")
        mock_redis.smembers.assert_called_once_with("testproject:dev:myset")

    @pytest.mark.asyncio
    async def test_sdiff_prefixes_all_keys(self, namespaced_redis, mock_redis):
        """Test that sdiff() prefixes all set keys."""
        mock_redis.sdiff.return_value = {"a", "b"}
        result = await namespaced_redis.sdiff("set1", "set2", "set3")
        mock_redis.sdiff.assert_called_once_with(
            "testproject:dev:set1", "testproject:dev:set2", "testproject:dev:set3"
        )
        assert result == {"a", "b"}

    @pytest.mark.asyncio
    async def test_sdiffstore_prefixes_all_keys(self, namespaced_redis, mock_redis):
        """Test that sdiffstore() prefixes destination and all source keys."""
        mock_redis.sdiffstore.return_value = 2
        result = await namespaced_redis.sdiffstore("dest", "set1", "set2", "set3")
        mock_redis.sdiffstore.assert_called_once_with(
            "testproject:dev:dest",
            "testproject:dev:set1",
            "testproject:dev:set2",
            "testproject:dev:set3",
        )
        assert result == 2


class TestNamespacedRedisSortedSetOperations:
    """Test sorted set operations with namespace prefixing."""

    @pytest.mark.asyncio
    async def test_zadd_prefixes_name(self, namespaced_redis, mock_redis):
        """Test that zadd() prefixes the sorted set name."""
        await namespaced_redis.zadd("myzset", {"member1": 1.0, "member2": 2.0})
        mock_redis.zadd.assert_called_once_with(
            "testproject:dev:myzset",
            {"member1": 1.0, "member2": 2.0},
            nx=False,
            xx=False,
        )

    @pytest.mark.asyncio
    async def test_zrange_prefixes_name(self, namespaced_redis, mock_redis):
        """Test that zrange() prefixes the sorted set name."""
        await namespaced_redis.zrange("myzset", 0, -1, withscores=True)
        mock_redis.zrange.assert_called_once_with(
            "testproject:dev:myzset", 0, -1, withscores=True
        )


class TestNamespacedRedisKeys:
    """Test keys() operation with namespace handling."""

    @pytest.mark.asyncio
    async def test_keys_prefixes_pattern(self, namespaced_redis, mock_redis):
        """Test that keys() prefixes the pattern."""
        mock_redis.keys.return_value = [
            "testproject:dev:user:1",
            "testproject:dev:user:2",
        ]
        result = await namespaced_redis.keys("user:*")
        mock_redis.keys.assert_called_once_with("testproject:dev:user:*")
        assert result == ["user:1", "user:2"]

    @pytest.mark.asyncio
    async def test_keys_returns_unprefixed_keys(self, namespaced_redis, mock_redis):
        """Test that keys() returns keys without the prefix."""
        mock_redis.keys.return_value = [
            "testproject:dev:cache:session:abc",
            "testproject:dev:cache:session:def",
        ]
        result = await namespaced_redis.keys("cache:session:*")
        assert result == ["cache:session:abc", "cache:session:def"]


class TestNamespacedRedisProperties:
    """Test NamespacedRedis properties."""

    def test_raw_property_returns_underlying_client(self, namespaced_redis, mock_redis):
        """Test that raw property returns the underlying Redis client."""
        assert namespaced_redis.raw is mock_redis

    def test_prefix_property_returns_prefix(self, namespaced_redis):
        """Test that prefix property returns the configured prefix."""
        assert namespaced_redis.prefix == "testproject:dev:"


class TestNamespacedPipeline:
    """Test NamespacedPipeline operations."""

    @pytest.fixture
    def mock_pipeline(self):
        """Create a mock pipeline."""
        return AsyncMock()

    @pytest.fixture
    def namespaced_pipeline(self, mock_pipeline):
        """Create a NamespacedPipeline instance."""
        return NamespacedPipeline(mock_pipeline, "testproject:dev:")

    def test_get_prefixes_key(self, namespaced_pipeline, mock_pipeline):
        """Test that pipeline get() prefixes the key."""
        namespaced_pipeline.get("mykey")
        mock_pipeline.get.assert_called_once_with("testproject:dev:mykey")

    def test_set_prefixes_key(self, namespaced_pipeline, mock_pipeline):
        """Test that pipeline set() prefixes the key."""
        namespaced_pipeline.set("mykey", "myvalue", ex=60)
        mock_pipeline.set.assert_called_once_with(
            "testproject:dev:mykey", "myvalue", ex=60, px=None
        )

    def test_methods_return_self_for_chaining(self, namespaced_pipeline):
        """Test that pipeline methods return self for chaining."""
        result = namespaced_pipeline.get("key1").set("key2", "value").incr("counter")
        assert result is namespaced_pipeline

    @pytest.mark.asyncio
    async def test_execute_calls_underlying_pipeline(
        self, namespaced_pipeline, mock_pipeline
    ):
        """Test that execute() calls the underlying pipeline."""
        mock_pipeline.execute.return_value = ["result1", "result2"]
        result = await namespaced_pipeline.execute()
        mock_pipeline.execute.assert_called_once()
        assert result == ["result1", "result2"]


class TestDifferentPrefixes:
    """Test NamespacedRedis with different prefix formats."""

    @pytest.mark.asyncio
    async def test_prod_prefix_format(self, mock_redis):
        """Test with production prefix format (no env suffix)."""
        redis = NamespacedRedis(mock_redis, "myproject:")
        await redis.get("mykey")
        mock_redis.get.assert_called_once_with("myproject:mykey")

    @pytest.mark.asyncio
    async def test_dev_prefix_format(self, mock_redis):
        """Test with dev prefix format."""
        redis = NamespacedRedis(mock_redis, "myproject:dev:")
        await redis.get("mykey")
        mock_redis.get.assert_called_once_with("myproject:dev:mykey")

    @pytest.mark.asyncio
    async def test_complex_key_names(self, mock_redis):
        """Test with complex key names containing colons."""
        redis = NamespacedRedis(mock_redis, "app:dev:")
        await redis.get("cache:user:123:profile")
        mock_redis.get.assert_called_once_with("app:dev:cache:user:123:profile")
