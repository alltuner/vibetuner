# ABOUTME: Tests for the robust_cron decorator.
# ABOUTME: Verifies cron tab forwarding, config registration, and retry integration.
# ruff: noqa: S101

from unittest.mock import MagicMock, patch

import pytest
import vibetuner.tasks.robust as robust_mod
from vibetuner.tasks.robust import _configs, robust_cron


@pytest.fixture(autouse=True)
def _reset_middleware_state():
    """Reset module-level middleware state between tests."""
    robust_mod._middleware_registered = False
    _configs.clear()
    yield
    robust_mod._middleware_registered = False
    _configs.clear()


def _make_mock_worker():
    """Create a mock worker with cron and middleware attributes."""
    worker = MagicMock()
    worker.middleware = lambda fn: fn

    def fake_cron(tab, *, max_tries=3, name=None, timeout=None, **kwargs):
        def decorator(fn):
            fn._cron_tab = tab
            fn._cron_name = name
            fn._cron_max_tries = max_tries
            fn._cron_timeout = timeout
            fn._cron_kwargs = kwargs
            return fn

        return decorator

    worker.cron = fake_cron
    return worker


class TestRobustCron:
    """Tests for the robust_cron decorator."""

    @patch("vibetuner.tasks.worker.get_worker")
    def test_registers_config_with_function_name(self, mock_get_worker):
        worker = _make_mock_worker()
        mock_get_worker.return_value = worker

        @robust_cron("*/15 * * * *")
        async def refresh_caches():
            pass

        assert "refresh_caches" in _configs
        config = _configs["refresh_caches"]
        assert config.max_retries == 3
        assert config.backoff_base == 2.0
        assert config.backoff_max == 300.0
        assert config.on_failure is None

    @patch("vibetuner.tasks.worker.get_worker")
    def test_registers_config_with_custom_name(self, mock_get_worker):
        worker = _make_mock_worker()
        mock_get_worker.return_value = worker

        @robust_cron("0 * * * *", name="my_cron")
        async def some_function():
            pass

        assert "my_cron" in _configs
        assert "some_function" not in _configs

    @patch("vibetuner.tasks.worker.get_worker")
    def test_forwards_cron_tab_to_worker(self, mock_get_worker):
        worker = _make_mock_worker()
        mock_get_worker.return_value = worker

        @robust_cron("*/5 * * * *")
        async def my_cron():
            pass

        assert my_cron._cron_tab == "*/5 * * * *"

    @patch("vibetuner.tasks.worker.get_worker")
    def test_forwards_max_retries_as_max_tries(self, mock_get_worker):
        worker = _make_mock_worker()
        mock_get_worker.return_value = worker

        @robust_cron("0 * * * *", max_retries=5)
        async def my_cron():
            pass

        assert my_cron._cron_max_tries == 5

    @patch("vibetuner.tasks.worker.get_worker")
    def test_forwards_timeout(self, mock_get_worker):
        worker = _make_mock_worker()
        mock_get_worker.return_value = worker

        @robust_cron("0 * * * *", timeout=60)
        async def my_cron():
            pass

        assert my_cron._cron_timeout == 60

    @patch("vibetuner.tasks.worker.get_worker")
    def test_custom_retry_config(self, mock_get_worker):
        worker = _make_mock_worker()
        mock_get_worker.return_value = worker

        callback = MagicMock()

        @robust_cron(
            "0 0 * * *",
            max_retries=5,
            backoff_base=3.0,
            backoff_max=120.0,
            on_failure=callback,
        )
        async def nightly_job():
            pass

        config = _configs["nightly_job"]
        assert config.max_retries == 5
        assert config.backoff_base == 3.0
        assert config.backoff_max == 120.0
        assert config.on_failure is callback

    @patch("vibetuner.tasks.worker.get_worker")
    def test_forwards_extra_kwargs_to_worker_cron(self, mock_get_worker):
        worker = _make_mock_worker()
        mock_get_worker.return_value = worker

        @robust_cron("0 * * * *", unique=False)
        async def my_cron():
            pass

        assert my_cron._cron_kwargs.get("unique") is False

    @patch("vibetuner.tasks.worker.get_worker")
    def test_rejects_non_string_name(self, mock_get_worker):
        worker = _make_mock_worker()
        mock_get_worker.return_value = worker

        with pytest.raises(TypeError, match="task name must be a string"):

            @robust_cron("0 * * * *", name=123)
            async def my_cron():
                pass

    @patch("vibetuner.tasks.worker.get_worker")
    def test_ensures_middleware_registered(self, mock_get_worker):
        worker = MagicMock()
        captured = []
        worker.middleware = lambda fn: captured.append(fn) or fn
        worker.cron = _make_mock_worker().cron
        mock_get_worker.return_value = worker

        @robust_cron("0 * * * *")
        async def my_cron():
            pass

        assert len(captured) == 1
