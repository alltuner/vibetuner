# ABOUTME: Tests that the session-scoped _vibetuner_redis_session fixture overrides
# ABOUTME: settings.redis_url with resolved_test_redis_url and restores it on teardown.
# ruff: noqa: S101
from unittest.mock import AsyncMock, patch

import pytest
from vibetuner.config import settings


async def _run_session_fixture():
    """Drive the autouse ``_vibetuner_redis_session`` body directly.

    Bypasses the pytest fixture decorator so the test exercises the exact
    setup/teardown path and can assert on ``settings.redis_url`` while the
    fixture is "active".
    """
    from vibetuner.testing import _vibetuner_redis_session

    gen = _vibetuner_redis_session.__wrapped__()
    await gen.__anext__()
    active_url = settings.redis_url
    with pytest.raises(StopAsyncIteration):
        await gen.__anext__()
    return active_url


@pytest.mark.unit
class TestVibetunerRedisSessionFixture:
    """The session-scoped Redis fixture must:

    - Point ``settings.redis_url`` at ``resolved_test_redis_url`` while active.
    - Close the shared client on setup and teardown so it reconnects to the
      test Redis.
    - Restore the original ``redis_url`` on teardown.
    """

    async def test_prefers_test_redis_url_and_restores(self):
        close_mock = AsyncMock()
        with (
            patch.object(settings, "redis_url", "redis://prod-host:6379/0"),
            patch.object(settings, "test_redis_url", "redis://localhost:6380/0"),
            patch("vibetuner.redis.close_redis_client", close_mock),
        ):
            active_url = await _run_session_fixture()

            assert str(active_url) == "redis://localhost:6380/0"
            assert close_mock.await_count == 2  # setup + teardown
            # Original restored after teardown.
            assert str(settings.redis_url) == "redis://prod-host:6379/0"

    async def test_falls_back_to_redis_url_when_test_unset(self):
        with (
            patch.object(settings, "redis_url", "redis://prod-host:6379/0"),
            patch.object(settings, "test_redis_url", None),
            patch("vibetuner.redis.close_redis_client", AsyncMock()),
        ):
            active_url = await _run_session_fixture()

            assert str(active_url) == "redis://prod-host:6379/0"
