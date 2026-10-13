# ABOUTME: Tests for the `vibetuner worker-health` CLI command.
# ABOUTME: Verifies exit codes and Redis client cleanup around the live-worker lookup.
# ruff: noqa: S101, S603
import subprocess
import sys
import textwrap
from unittest.mock import AsyncMock, MagicMock, patch

from typer.testing import CliRunner
from vibetuner.cli import app


runner = CliRunner()


class FakeRedis:
    """Async Redis stand-in that only records being closed."""

    def __init__(self) -> None:
        self.closed = False

    async def aclose(self) -> None:
        self.closed = True


def _settings(workers_available: bool = True) -> MagicMock:
    s = MagicMock()
    s.workers_available = workers_available
    s.redis_url = "redis://localhost:6379/0"
    s.redis_key_prefix = "myproject:"
    return s


class TestWorkerHealth:
    def test_healthy_when_a_worker_is_live(self):
        fake = FakeRedis()
        lookup = AsyncMock(return_value=True)
        with (
            patch("vibetuner.config.settings", _settings()),
            patch("redis.asyncio.from_url", return_value=fake),
            patch("vibetuner.cli.health.has_live_worker", lookup),
        ):
            result = runner.invoke(app, ["worker-health"])
        assert result.exit_code == 0
        lookup.assert_awaited_once_with(fake, "myproject")
        assert fake.closed is True

    def test_unhealthy_when_no_worker_is_live(self):
        fake = FakeRedis()
        with (
            patch("vibetuner.config.settings", _settings()),
            patch("redis.asyncio.from_url", return_value=fake),
            patch(
                "vibetuner.cli.health.has_live_worker",
                AsyncMock(return_value=False),
            ),
        ):
            result = runner.invoke(app, ["worker-health"])
        assert result.exit_code == 1
        assert fake.closed is True

    def test_unhealthy_when_redis_not_configured(self):
        with patch("vibetuner.config.settings", _settings(workers_available=False)):
            result = runner.invoke(app, ["worker-health"])
        assert result.exit_code == 1

    def test_unhealthy_when_redis_errors(self):
        fake = FakeRedis()
        with (
            patch("vibetuner.config.settings", _settings()),
            patch("redis.asyncio.from_url", return_value=fake),
            patch(
                "vibetuner.cli.health.has_live_worker",
                AsyncMock(side_effect=ConnectionError("boom")),
            ),
        ):
            result = runner.invoke(app, ["worker-health"])
        assert result.exit_code == 1
        assert fake.closed is True


class TestWorkerHealthFastPath:
    """The healthcheck must skip the full CLI/app bootstrap so it finishes
    well under a container healthcheck timeout."""

    def test_main_dispatches_without_building_full_app(self):
        # Run in a fresh interpreter: module import state is process-global,
        # and other tests import vibetuner.cli.root (the heavy Typer app).
        script = textwrap.dedent(
            """
            import sys
            sys.argv = ["vibetuner", "worker-health"]

            import vibetuner.cli as cli
            import vibetuner.cli.health as health

            async def fake_check():
                return 0

            health.check_worker = fake_check

            try:
                cli.main()
            except SystemExit as exc:
                assert exc.code == 0, exc.code

            # The fast path must not import the heavy command tree, which is
            # what pulls in the user's tune.py via load_app_config().
            assert "vibetuner.cli.root" not in sys.modules
            assert "vibetuner.cli.scaffold" not in sys.modules
            print("OK")
            """
        )
        result = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            check=False,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        assert "OK" in result.stdout
