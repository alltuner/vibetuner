# ABOUTME: Tests for the task worker lifespan.
# ABOUTME: Verifies that core services are initialized during worker startup.
"""Tests for the task worker lifespan."""

from unittest.mock import AsyncMock, patch

import pytest


class TestWorkerBaseLifespan:
    """Tests for the worker's base_lifespan."""

    @pytest.mark.asyncio
    async def test_base_lifespan_initializes_runtime_config_cache(self):
        """base_lifespan calls RuntimeConfig.refresh_cache() after MongoDB init."""
        with (
            patch("vibetuner.tasks.lifespan.init_mongodb", new_callable=AsyncMock),
            patch("vibetuner.tasks.lifespan.init_sqlmodel", new_callable=AsyncMock),
            patch(
                "vibetuner.tasks.lifespan.teardown_mongodb",
                new_callable=AsyncMock,
            ),
            patch(
                "vibetuner.tasks.lifespan.teardown_sqlmodel",
                new_callable=AsyncMock,
            ),
            patch("vibetuner.tasks.lifespan.settings") as mock_settings,
            patch("vibetuner.tasks.lifespan.RuntimeConfig") as mock_runtime_config,
        ):
            mock_settings.mongodb_url = "mongodb://localhost:27017"
            mock_settings.worker_watchdog_timeout = 0
            mock_runtime_config.refresh_cache = AsyncMock()

            from vibetuner.tasks.lifespan import base_lifespan

            async with base_lifespan():
                pass

            mock_runtime_config.refresh_cache.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_base_lifespan_skips_runtime_config_without_mongodb(self):
        """base_lifespan skips RuntimeConfig.refresh_cache() when no MongoDB URL."""
        with (
            patch("vibetuner.tasks.lifespan.init_mongodb", new_callable=AsyncMock),
            patch("vibetuner.tasks.lifespan.init_sqlmodel", new_callable=AsyncMock),
            patch(
                "vibetuner.tasks.lifespan.teardown_mongodb",
                new_callable=AsyncMock,
            ),
            patch(
                "vibetuner.tasks.lifespan.teardown_sqlmodel",
                new_callable=AsyncMock,
            ),
            patch("vibetuner.tasks.lifespan.settings") as mock_settings,
            patch("vibetuner.tasks.lifespan.RuntimeConfig") as mock_runtime_config,
        ):
            mock_settings.mongodb_url = None
            mock_settings.worker_watchdog_timeout = 0
            mock_runtime_config.refresh_cache = AsyncMock()

            from vibetuner.tasks.lifespan import base_lifespan

            async with base_lifespan():
                pass

            mock_runtime_config.refresh_cache.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_base_lifespan_starts_and_stops_watchdog(self):
        """The liveness watchdog is started and stopped when enabled."""
        with (
            patch("vibetuner.tasks.lifespan.init_mongodb", new_callable=AsyncMock),
            patch("vibetuner.tasks.lifespan.init_sqlmodel", new_callable=AsyncMock),
            patch("vibetuner.tasks.lifespan.teardown_mongodb", new_callable=AsyncMock),
            patch("vibetuner.tasks.lifespan.teardown_sqlmodel", new_callable=AsyncMock),
            patch("vibetuner.tasks.lifespan.settings") as mock_settings,
            patch("vibetuner.tasks.lifespan.LoopWatchdog") as mock_watchdog_cls,
        ):
            mock_settings.mongodb_url = None
            mock_settings.worker_watchdog_timeout = 60.0
            mock_settings.worker_watchdog_interval = 5.0
            instance = mock_watchdog_cls.return_value
            instance.stop = AsyncMock()

            from vibetuner.tasks.lifespan import base_lifespan

            async with base_lifespan():
                instance.start.assert_called_once()
                instance.stop.assert_not_awaited()

            instance.stop.assert_awaited_once()
