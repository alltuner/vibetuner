# ABOUTME: Tests for the `vibetuner worker-health` CLI command.
# ABOUTME: Verifies exit codes based on the presence of a fresh streaq health key.
# ruff: noqa: S101
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner
from vibetuner.cli import app


runner = CliRunner()


class FakeRedis:
    """Minimal async Redis stand-in for the health check."""

    def __init__(self, keys: list[str], scan_error: Exception | None = None) -> None:
        self._keys = keys
        self._scan_error = scan_error
        self.closed = False

    def scan_iter(self, match=None, count=None):
        keys = self._keys
        error = self._scan_error

        async def gen():
            if error is not None:
                raise error
            for key in keys:
                yield key

        return gen()

    async def aclose(self) -> None:
        self.closed = True


def _settings(workers_available: bool = True) -> MagicMock:
    s = MagicMock()
    s.workers_available = workers_available
    s.redis_url = "redis://localhost:6379/0"
    s.redis_key_prefix = "myproject:"
    return s


class TestWorkerHealth:
    def test_healthy_when_health_key_exists(self):
        fake = FakeRedis(keys=["streaq:myproject:health:abc123"])
        with (
            patch("vibetuner.config.settings", _settings()),
            patch("redis.asyncio.from_url", return_value=fake),
        ):
            result = runner.invoke(app, ["worker-health"])
        assert result.exit_code == 0
        assert fake.closed is True

    def test_unhealthy_when_no_health_key(self):
        fake = FakeRedis(keys=[])
        with (
            patch("vibetuner.config.settings", _settings()),
            patch("redis.asyncio.from_url", return_value=fake),
        ):
            result = runner.invoke(app, ["worker-health"])
        assert result.exit_code == 1
        assert fake.closed is True

    def test_unhealthy_when_redis_not_configured(self):
        with patch("vibetuner.config.settings", _settings(workers_available=False)):
            result = runner.invoke(app, ["worker-health"])
        assert result.exit_code == 1

    def test_unhealthy_when_redis_errors(self):
        fake = FakeRedis(keys=[], scan_error=ConnectionError("boom"))
        with (
            patch("vibetuner.config.settings", _settings()),
            patch("redis.asyncio.from_url", return_value=fake),
        ):
            result = runner.invoke(app, ["worker-health"])
        assert result.exit_code == 1
        assert fake.closed is True
