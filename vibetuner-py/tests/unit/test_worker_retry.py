# ABOUTME: Tests for the streaq worker's coredis retry policy.
# ABOUTME: Verifies a Redis LOADING reply is waited out and that waiting is bounded.
"""Tests for vibetuner.worker_retry."""

# ruff: noqa: S101

import pytest
from coredis.exceptions import BusyLoadingError, ConnectionError as RedisConnectionError
from vibetuner.worker_retry import LOADING_MAX_DELAY, worker_retry_policy


class FakeClock:
    """Monotonic clock that only advances when a retry sleeps."""

    def __init__(self) -> None:
        self.now = 0.0

    def monotonic(self) -> float:
        return self.now


@pytest.fixture
def delays(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """Record retry delays instead of waiting for them, advancing a fake clock."""
    clock = FakeClock()
    recorded: list[float] = []

    async def fake_sleep(seconds: float) -> None:
        recorded.append(seconds)
        clock.now += seconds

    monkeypatch.setattr("coredis.retry.sleep", fake_sleep)
    monkeypatch.setattr("coredis.retry.time", clock)
    return recorded


class TestWorkerRetryPolicy:
    """The policy passed to the worker's coredis client."""

    async def test_waits_out_a_loading_reply(
        self, delays: list[float], log_sink: list[str]
    ) -> None:
        """A Redis that answers LOADING is retried until it finishes loading."""
        attempts = 0

        async def loading_then_ready() -> str:
            nonlocal attempts
            attempts += 1
            if attempts <= 4:
                raise BusyLoadingError("Redis is loading the dataset in memory")
            return "ready"

        policy = worker_retry_policy(300.0)

        assert await policy.call_with_retries(loading_then_ready) == "ready"
        # coredis's own default policy gives up after 2 retries 10ms apart.
        assert attempts == 5
        assert len(delays) == 4
        assert all(0.5 <= delay <= 5.0 for delay in delays)
        assert any("loading" in message.lower() for message in log_sink)

    async def test_stops_waiting_at_the_deadline(self, delays: list[float]) -> None:
        """Waiting is bounded, so a Redis stuck in LOADING is not masked forever."""

        async def always_loading() -> str:
            raise BusyLoadingError("Redis is loading the dataset in memory")

        loading_timeout = 30.0
        policy = worker_retry_policy(loading_timeout)

        with pytest.raises(BusyLoadingError):
            await policy.call_with_retries(always_loading)
        # The jittered delay is drawn again for the sleep the deadline check
        # approved, so the total can overshoot by at most one backoff.
        assert sum(delays) <= loading_timeout + LOADING_MAX_DELAY

    async def test_an_unreachable_redis_is_not_waited_out(
        self, delays: list[float]
    ) -> None:
        """A plain connection error keeps coredis's fast give-up behaviour."""
        attempts = 0

        async def always_refused() -> str:
            nonlocal attempts
            attempts += 1
            raise RedisConnectionError("Connection refused")

        policy = worker_retry_policy(300.0)

        with pytest.raises(RedisConnectionError):
            await policy.call_with_retries(always_refused)
        assert attempts == 3
        assert sum(delays) < 0.1
