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
            patch(
                "vibetuner.tasks.lifespan.init_mongodb", new_callable=AsyncMock
            ),
            patch(
                "vibetuner.tasks.lifespan.init_sqlmodel", new_callable=AsyncMock
            ),
            patch(
                "vibetuner.tasks.lifespan.teardown_mongodb",
                new_callable=AsyncMock,
            ),
            patch(
                "vibetuner.tasks.lifespan.teardown_sqlmodel",
                new_callable=AsyncMock,
            ),
            patch("vibetuner.tasks.lifespan.settings") as mock_settings,
            patch(
                "vibetuner.tasks.lifespan.RuntimeConfig"
            ) as mock_runtime_config,
        ):
            mock_settings.mongodb_url = "mongodb://localhost:27017"
            mock_runtime_config.refresh_cache = AsyncMock()

            from vibetuner.tasks.lifespan import base_lifespan

            async with base_lifespan():
                pass

            mock_runtime_config.refresh_cache.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_base_lifespan_skips_runtime_config_without_mongodb(self):
        """base_lifespan skips RuntimeConfig.refresh_cache() when no MongoDB URL."""
        with (
            patch(
                "vibetuner.tasks.lifespan.init_mongodb", new_callable=AsyncMock
            ),
            patch(
                "vibetuner.tasks.lifespan.init_sqlmodel", new_callable=AsyncMock
            ),
            patch(
                "vibetuner.tasks.lifespan.teardown_mongodb",
                new_callable=AsyncMock,
            ),
            patch(
                "vibetuner.tasks.lifespan.teardown_sqlmodel",
                new_callable=AsyncMock,
            ),
            patch("vibetuner.tasks.lifespan.settings") as mock_settings,
            patch(
                "vibetuner.tasks.lifespan.RuntimeConfig"
            ) as mock_runtime_config,
        ):
            mock_settings.mongodb_url = None
            mock_runtime_config.refresh_cache = AsyncMock()

            from vibetuner.tasks.lifespan import base_lifespan

            async with base_lifespan():
                pass

            mock_runtime_config.refresh_cache.assert_not_awaited()
