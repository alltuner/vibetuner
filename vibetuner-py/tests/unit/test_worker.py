# ABOUTME: Tests for the streaq worker construction.
# ABOUTME: Verifies Redis connection-resilience kwargs are passed to the worker.
"""Tests for the streaq worker module."""

# ruff: noqa: S101

import importlib
from unittest.mock import MagicMock, patch


class TestWorkerConstruction:
    """Verify how the module-level worker is built from settings."""

    def test_passes_worker_redis_kwargs(self):
        """The worker is constructed with the configured resilience kwargs."""
        resilience = {"stream_timeout": 30.0, "socket_keepalive": True}
        fake_settings = MagicMock()
        fake_settings.workers_available = True
        fake_settings.redis_url = "redis://localhost:6379/0"
        fake_settings.worker_redis_kwargs = resilience
        fake_settings.redis_key_prefix = "myproject:"
        fake_settings.worker_concurrency = 16

        with (
            patch("vibetuner.config.settings", fake_settings),
            patch("streaq.Worker") as mock_worker,
        ):
            import vibetuner.tasks.worker as worker_mod

            importlib.reload(worker_mod)

        assert mock_worker.call_args.kwargs["redis_kwargs"] is resilience

        # Restore the module to its real state for other tests.
        importlib.reload(worker_mod)

    def test_no_worker_when_redis_not_configured(self):
        """No worker is built when Redis is unavailable."""
        fake_settings = MagicMock()
        fake_settings.workers_available = False

        with (
            patch("vibetuner.config.settings", fake_settings),
            patch("streaq.Worker") as mock_worker,
        ):
            import vibetuner.tasks.worker as worker_mod

            importlib.reload(worker_mod)
            assert worker_mod.worker is None
            mock_worker.assert_not_called()

        # Restore the module to its real state for other tests.
        importlib.reload(worker_mod)
