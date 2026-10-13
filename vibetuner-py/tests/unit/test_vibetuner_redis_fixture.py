# ABOUTME: Tests the Redis fixtures: the session one points redis_url at the test Redis,
# ABOUTME: the per-test one closes a shared client the test created on that test's loop.
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


async def _run_test_fixture(client_created_during_test: object | None) -> None:
    """Drive the autouse per-test ``_vibetuner_redis_client`` body directly,
    simulating a test that leaves ``client_created_during_test`` as the shared
    client (or leaves the shared client untouched when ``None``).
    """
    import vibetuner.redis as redis_mod
    from vibetuner.testing import _vibetuner_redis_client

    gen = _vibetuner_redis_client.__wrapped__()
    await gen.__anext__()
    if client_created_during_test is not None:
        redis_mod._client = client_created_during_test
    with pytest.raises(StopAsyncIteration):
        await gen.__anext__()


@pytest.mark.unit
class TestVibetunerRedisClientFixture:
    """The per-test Redis fixture closes the shared client only when the test
    created it, so the client is closed on the event loop it is bound to.
    """

    async def test_closes_client_created_during_test(self):
        import vibetuner.redis as redis_mod

        created = AsyncMock()
        with patch.object(redis_mod, "_client", None):
            await _run_test_fixture(created)

            created.aclose.assert_awaited_once()
            assert redis_mod._client is None

    async def test_leaves_client_created_before_test_open(self):
        import vibetuner.redis as redis_mod

        existing = AsyncMock()
        with patch.object(redis_mod, "_client", existing):
            await _run_test_fixture(None)

            existing.aclose.assert_not_awaited()
            assert redis_mod._client is existing
