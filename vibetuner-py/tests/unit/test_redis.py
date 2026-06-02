# ruff: noqa: S101
"""Tests for the shared Redis client module."""

from unittest.mock import AsyncMock, patch

import pytest
import vibetuner.redis as redis_mod


class TestGetRedisClient:
    """Test lazy initialization of the shared Redis client."""

    @pytest.mark.asyncio
    async def test_returns_none_when_no_redis_url(self):
        """Returns None if redis_url is not configured."""
        redis_mod._client = None
        with patch("vibetuner.config.settings") as mock_settings:
            mock_settings.redis_url = None
            result = await redis_mod.get_redis_client()
        assert result is None

    @pytest.mark.asyncio
    async def test_creates_client_when_url_configured(self):
        """Creates and caches a command client with resilience kwargs when set."""
        redis_mod._client = None
        mock_client = AsyncMock()

        with (
            patch("vibetuner.config.settings") as mock_settings,
            patch("redis.asyncio.from_url", return_value=mock_client) as mock_from_url,
        ):
            mock_settings.redis_url = "redis://localhost:6379/0"
            mock_settings.redis_client_kwargs = {"socket_timeout": 30.0}
            result = await redis_mod.get_redis_client()

        assert result is mock_client
        mock_from_url.assert_called_once_with(
            "redis://localhost:6379/0", socket_timeout=30.0
        )

        # Cleanup
        redis_mod._client = None

    @pytest.mark.asyncio
    async def test_reuses_cached_client(self):
        """Returns the same client on subsequent calls."""
        mock_client = AsyncMock()
        redis_mod._client = mock_client

        result = await redis_mod.get_redis_client()
        assert result is mock_client

        # Cleanup
        redis_mod._client = None


class TestCloseRedisClient:
    """Test client shutdown."""

    @pytest.mark.asyncio
    async def test_closes_and_clears(self):
        """Closes the client and sets it to None."""
        mock_client = AsyncMock()
        redis_mod._client = mock_client

        await redis_mod.close_redis_client()

        mock_client.aclose.assert_called_once()
        assert redis_mod._client is None

    @pytest.mark.asyncio
    async def test_noop_when_no_client(self):
        """Does nothing if no client exists."""
        redis_mod._client = None
        await redis_mod.close_redis_client()
        assert redis_mod._client is None


class TestResetRedisClient:
    """Test client reset after connection errors."""

    def test_resets_to_none(self):
        redis_mod._client = AsyncMock()
        redis_mod.reset_redis_client()
        assert redis_mod._client is None


class TestCreateRedisClient:
    """Test the dedicated pub/sub subscriber client factory."""

    def test_returns_none_when_no_redis_url(self):
        """Returns None if redis_url is not configured."""
        with patch("vibetuner.config.settings") as mock_settings:
            mock_settings.redis_url = None
            assert redis_mod.create_redis_client() is None

    def test_uses_timeout_free_subscriber_kwargs(self):
        """The subscriber client is built with the timeout-free subscriber kwargs."""
        mock_client = object()
        with (
            patch("vibetuner.config.settings") as mock_settings,
            patch("redis.asyncio.from_url", return_value=mock_client) as mock_from_url,
        ):
            mock_settings.redis_url = "redis://localhost:6379/0"
            mock_settings.redis_subscriber_kwargs = {"socket_timeout": None}
            result = redis_mod.create_redis_client()

        assert result is mock_client
        mock_from_url.assert_called_once_with(
            "redis://localhost:6379/0", socket_timeout=None
        )
