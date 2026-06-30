# ABOUTME: Unit tests for SSE event buffer and transport layer
# ABOUTME: Tests ring buffer, event ID assignment, replay logic, and channel streaming resumption
# ruff: noqa: S101

import asyncio
import contextlib
import json
from unittest.mock import patch

import pytest
import pytest_asyncio
from fastapi import APIRouter, Request
from starlette.requests import Request as StarletteRequest
from vibetuner.sse import (
    _LISTENER_RECONNECT_CAP_DELAY,
    _LISTENER_RECONNECT_DELAY,
    _WORKER_ID,
    _channel_buffers,
    _dispatch_local,
    _EventBuffer,
    _format_event,
    _next_reconnect_delay,
    _parse_redis_message,
    _publish_to_redis,
    _stream_from_channel,
    sse_endpoint,
    start_redis_listener,
)


def _make_request(path: str = "/events") -> StarletteRequest:
    """Build a minimal ASGI GET request for invoking an SSE endpoint directly."""
    return StarletteRequest(
        {
            "type": "http",
            "method": "GET",
            "path": path,
            "headers": [],
            "query_string": b"",
        }
    )


class TestEventBuffer:
    def test_append_assigns_incrementing_ids(self):
        buf = _EventBuffer(maxlen=10)
        id1 = buf.append({"event": "msg", "data": "a"})
        id2 = buf.append({"event": "msg", "data": "b"})
        assert id1 == 1
        assert id2 == 2

    def test_events_after_returns_events_with_id_greater_than(self):
        buf = _EventBuffer(maxlen=10)
        buf.append({"event": "msg", "data": "a"})
        buf.append({"event": "msg", "data": "b"})
        buf.append({"event": "msg", "data": "c"})
        result = buf.events_after(1)
        assert len(result) == 2
        assert result[0] == (2, {"event": "msg", "data": "b"})
        assert result[1] == (3, {"event": "msg", "data": "c"})

    def test_events_after_zero_returns_all(self):
        buf = _EventBuffer(maxlen=10)
        buf.append({"event": "msg", "data": "a"})
        buf.append({"event": "msg", "data": "b"})
        result = buf.events_after(0)
        assert len(result) == 2

    def test_events_after_latest_returns_empty(self):
        buf = _EventBuffer(maxlen=10)
        buf.append({"event": "msg", "data": "a"})
        result = buf.events_after(1)
        assert result == []

    def test_ring_buffer_evicts_oldest(self):
        buf = _EventBuffer(maxlen=3)
        buf.append({"event": "msg", "data": "a"})  # id=1
        buf.append({"event": "msg", "data": "b"})  # id=2
        buf.append({"event": "msg", "data": "c"})  # id=3
        buf.append({"event": "msg", "data": "d"})  # id=4, evicts id=1
        result = buf.events_after(0)
        assert len(result) == 3
        assert result[0][0] == 2  # oldest remaining

    def test_events_after_evicted_id_returns_all_available(self):
        buf = _EventBuffer(maxlen=2)
        buf.append({"event": "msg", "data": "a"})  # id=1
        buf.append({"event": "msg", "data": "b"})  # id=2
        buf.append({"event": "msg", "data": "c"})  # id=3, evicts id=1
        # Requesting from evicted id=1 returns all available
        result = buf.events_after(1)
        assert len(result) == 2
        assert result[0][0] == 2


class TestFormatEvent:
    def test_formats_data_and_event(self):
        result = _format_event({"event": "update", "data": "hello"})
        assert b"event: update\n" in result
        assert b"data: hello\n" in result
        assert result.endswith(b"\n\n")

    def test_formats_with_id(self):
        result = _format_event({"event": "msg", "data": "hi"}, event_id="42")
        assert b"id: 42\n" in result

    def test_formats_comment_only(self):
        result = _format_event({"comment": "keepalive"})
        assert b": keepalive\n" in result

    def test_multiline_data(self):
        result = _format_event({"event": "msg", "data": "line1\nline2"})
        assert b"data: line1\n" in result
        assert b"data: line2\n" in result


class TestStreamFromChannelResumption:
    @staticmethod
    async def _collect_n(gen, n: int, timeout: float = 1.0) -> list[bytes]:
        """Collect n items from an async generator with timeout."""
        items = []
        async for item in gen:
            items.append(item)
            if len(items) >= n:
                break
        return items

    @pytest.mark.asyncio
    async def test_stream_replays_buffered_events(self):
        """When buffer exists and last_event_id is set, replay missed events."""
        ch = "test-replay"
        buf = _EventBuffer(maxlen=10)
        _channel_buffers[ch] = buf

        buf.append({"event": "msg", "data": "a"})
        buf.append({"event": "msg", "data": "b"})
        buf.append({"event": "msg", "data": "c"})

        try:
            gen = _stream_from_channel(ch, last_event_id=1)
            items = await asyncio.wait_for(self._collect_n(gen, 2), timeout=2.0)
            assert len(items) == 2
            assert b"data: b\n" in items[0]
            assert b"id: 2\n" in items[0]
            assert b"data: c\n" in items[1]
            assert b"id: 3\n" in items[1]
        finally:
            _channel_buffers.pop(ch, None)

    @pytest.mark.asyncio
    async def test_stream_without_resumption_has_no_replay(self):
        """When no last_event_id, stream starts from live events only."""
        ch = "test-no-replay"
        buf = _EventBuffer(maxlen=10)
        _channel_buffers[ch] = buf
        buf.append({"event": "msg", "data": "old"})

        try:
            gen = _stream_from_channel(ch)

            # Start the generator in a task so it subscribes to the channel
            async def collect():
                return await self._collect_n(gen, 1)

            task = asyncio.create_task(collect())
            # Yield control so the generator can reach its first await (_subscribe)
            await asyncio.sleep(0.05)

            # Push a live event after the generator is subscribed
            _dispatch_local(ch, {"event": "msg", "data": "live"})
            items = await asyncio.wait_for(task, timeout=2.0)
            assert b"data: live\n" in items[0]
            # Should NOT contain the old buffered event
            assert b"data: old\n" not in items[0]
        finally:
            _channel_buffers.pop(ch, None)


class TestSseEndpointBuffering:
    def test_sse_endpoint_with_buffer_size_creates_buffer(self):
        router = APIRouter()

        @sse_endpoint("/events", channel="buf-test", buffer_size=50, router=router)
        async def stream(request: Request):
            pass

        assert "buf-test" in _channel_buffers
        assert _channel_buffers["buf-test"]._buf.maxlen == 50

        # Cleanup
        _channel_buffers.pop("buf-test", None)

    def test_sse_endpoint_without_buffer_size_no_buffer(self):
        router = APIRouter()

        @sse_endpoint("/events2", channel="no-buf-test", router=router)
        async def stream(request: Request):
            pass

        assert "no-buf-test" not in _channel_buffers


class TestSseAntiBufferingHeaders:
    """SSE responses must defeat proxy/CDN buffering (Caddy, nginx, Cloudflare).

    Without these headers a buffering reverse proxy holds ``text/event-stream``
    responses, so the client sees a 200 that never delivers any bytes.
    """

    @pytest.mark.asyncio
    async def test_channel_response_disables_buffering(self):
        @sse_endpoint("/events-hdr-chan", channel="hdr-chan-test")
        async def stream(request: Request):
            pass

        response = await stream(request=_make_request("/events-hdr-chan"))
        try:
            assert response.headers["cache-control"] == "no-cache"
            assert response.headers["x-accel-buffering"] == "no"
        finally:
            await response.body_iterator.aclose()

    @pytest.mark.asyncio
    async def test_generator_response_disables_buffering(self):
        @sse_endpoint("/events-hdr-gen")
        async def stream(request: Request):
            yield {"event": "tick", "data": "ping"}

        response = await stream(request=_make_request("/events-hdr-gen"))
        try:
            assert response.headers["cache-control"] == "no-cache"
            assert response.headers["x-accel-buffering"] == "no"
        finally:
            await response.body_iterator.aclose()


def _redis_pmessage(prefix: str, channel: str, payload: dict) -> dict:
    """Build a Redis pmessage dict as redis-py delivers it to the listen loop."""
    return {
        "type": "pmessage",
        "pattern": f"{prefix}*".encode(),
        "channel": f"{prefix}{channel}".encode(),
        "data": json.dumps(payload).encode(),
    }


class TestRedisLoopbackDedup:
    """Origin tagging stops a worker from re-delivering events it published itself.

    ``broadcast()`` dispatches locally *and* publishes to Redis; the worker's own
    listener then receives that publish. Without a same-origin filter the local
    subscriber would see every event twice once the listener is reliably alive.
    """

    def test_parse_skips_own_published_message(self):
        msg = _redis_pmessage(
            "app:sse:",
            "room",
            {"event": "update", "data": "1", "_origin": _WORKER_ID},
        )
        assert _parse_redis_message(msg, "app:sse:") is None

    def test_parse_dispatches_foreign_message(self):
        msg = _redis_pmessage(
            "app:sse:",
            "room",
            {"event": "update", "data": "1", "_origin": "some-other-worker"},
        )
        parsed = _parse_redis_message(msg, "app:sse:")
        assert parsed is not None
        channel, payload = parsed
        assert channel == "room"
        assert payload == {"event": "update", "data": "1"}

    def test_parse_dispatches_message_without_origin(self):
        # Messages from a publisher that predates origin tagging must still flow.
        msg = _redis_pmessage("app:sse:", "room", {"event": "update", "data": "1"})
        parsed = _parse_redis_message(msg, "app:sse:")
        assert parsed is not None
        _, payload = parsed
        assert payload == {"event": "update", "data": "1"}

    @pytest.mark.asyncio
    async def test_publish_tags_message_with_worker_origin(self, monkeypatch):
        published: list[tuple[str, str]] = []

        class _Client:
            async def publish(self, channel: str, data: str) -> None:
                published.append((channel, data))

        import vibetuner.sse as sse

        monkeypatch.setattr(sse, "_redis_publish_client", _Client())
        await _publish_to_redis("room", {"event": "update", "data": "1"})

        assert len(published) == 1
        _, raw = published[0]
        sent = json.loads(raw)
        assert sent["event"] == "update"
        assert sent["data"] == "1"
        assert sent["_origin"] == _WORKER_ID


class _FakePubSub:
    def __init__(self) -> None:
        self.patterns: list[str] = []

    async def psubscribe(self, pattern: str) -> None:
        self.patterns.append(pattern)

    async def punsubscribe(self) -> None:
        pass

    async def listen(self):
        while True:
            await asyncio.sleep(3600)
            yield {}


class _FakeClient:
    def __init__(self) -> None:
        self._pubsub = _FakePubSub()

    def pubsub(self) -> _FakePubSub:
        return self._pubsub

    async def aclose(self) -> None:
        pass


class _FlakyPubSub:
    """A subscriber whose first connection's ``listen()`` raises a Redis error."""

    def __init__(self, fail: bool, subscribed: list[str], reconnected) -> None:
        self._fail = fail
        self._subscribed = subscribed
        self._reconnected = reconnected

    async def psubscribe(self, pattern: str) -> None:
        self._subscribed.append(pattern)
        if len(self._subscribed) >= 2:
            self._reconnected.set()

    async def punsubscribe(self) -> None:
        pass

    async def aclose(self) -> None:
        pass

    async def listen(self):
        from redis.exceptions import TimeoutError as RedisTimeoutError

        if self._fail:
            raise RedisTimeoutError("Timeout reading from localhost:6379")
        while True:
            await asyncio.sleep(3600)
            yield {}


class _FlakyClient:
    def __init__(self, fail: bool, subscribed: list[str], reconnected) -> None:
        self._pubsub = _FlakyPubSub(fail, subscribed, reconnected)

    def pubsub(self) -> _FlakyPubSub:
        return self._pubsub

    async def aclose(self) -> None:
        pass


def _enable_redis(monkeypatch) -> None:
    """Make ``settings.redis_url`` look configured so the listener task starts."""
    monkeypatch.setattr("vibetuner.config.settings.redis_url", "redis://localhost:6379")


@pytest_asyncio.fixture
async def sse_module():
    import vibetuner.sse as sse

    sse._redis_listener_task = None
    yield sse
    task = sse._redis_listener_task
    if task is not None:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task
    sse._redis_listener_task = None


class TestRedisListenerLifecycle:
    """The listener is a process-lifetime task, not tied to a single request.

    A dead task must be replaced; a live one must not be duplicated. Issue #1958
    was the lazy guard treating a dead-but-non-None task as still subscribed, so
    the worker never re-subscribed and ``PUBSUB NUMPAT`` decayed to 0.
    """

    @pytest.mark.asyncio
    async def test_start_is_idempotent_while_alive(self, sse_module, monkeypatch):
        sse = sse_module
        _enable_redis(monkeypatch)
        monkeypatch.setattr(
            "vibetuner.redis.create_redis_client", lambda: _FakeClient()
        )

        await start_redis_listener()
        first = sse._redis_listener_task
        assert first is not None and not first.done()

        await start_redis_listener()
        assert sse._redis_listener_task is first

    @pytest.mark.asyncio
    async def test_start_replaces_dead_task(self, sse_module, monkeypatch):
        sse = sse_module
        _enable_redis(monkeypatch)
        monkeypatch.setattr(
            "vibetuner.redis.create_redis_client", lambda: _FakeClient()
        )

        await start_redis_listener()
        first = sse._redis_listener_task
        assert first is not None

        first.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await first
        assert first.done()

        await start_redis_listener()
        second = sse._redis_listener_task
        assert second is not None and second is not first
        assert not second.done()

    @pytest.mark.asyncio
    async def test_no_task_without_redis_url(self, sse_module, monkeypatch):
        """With Redis unconfigured the listener stays local-only (no task)."""
        sse = sse_module
        monkeypatch.setattr("vibetuner.config.settings.redis_url", None)

        await start_redis_listener()
        assert sse._redis_listener_task is None

    @pytest.mark.asyncio
    async def test_listener_reconnects_after_redis_error(self, sse_module, monkeypatch):
        """A Redis error re-subscribes instead of killing the listener.

        Issue #1958: the subscriber's 30s read timeout raised TimeoutError on idle
        channels; the loop only caught CancelledError, so the task died and
        PUBSUB NUMPAT decayed to 0. The loop must reconnect and re-subscribe.
        """
        sse = sse_module
        _enable_redis(monkeypatch)
        monkeypatch.setattr(sse, "_LISTENER_RECONNECT_DELAY", 0)

        subscribed: list[str] = []
        reconnected = asyncio.Event()
        clients = iter(
            [
                _FlakyClient(fail=True, subscribed=subscribed, reconnected=reconnected),
                _FlakyClient(
                    fail=False, subscribed=subscribed, reconnected=reconnected
                ),
            ]
        )
        monkeypatch.setattr(
            "vibetuner.redis.create_redis_client", lambda: next(clients)
        )

        await start_redis_listener()
        await asyncio.wait_for(reconnected.wait(), timeout=2)
        assert len(subscribed) >= 2


class _PsubFailPubSub:
    """Fake pub/sub whose psubscribe raises RedisError until `fail_until` phases have passed."""

    def __init__(
        self, phase: int, done: asyncio.Event, real_sleep, fail_until: int
    ) -> None:
        self._phase = phase
        self._done = done
        self._real_sleep = real_sleep
        self._fail_until = fail_until

    async def psubscribe(self, _pattern: str) -> None:
        from redis.exceptions import RedisError

        if self._phase < self._fail_until:
            raise RedisError(f"psubscribe failure phase {self._phase}")

    async def aclose(self) -> None:
        pass

    async def listen(self):
        self._done.set()
        while True:
            await self._real_sleep(
                3600
            )  # real sleep so capturing_sleep isn't called here
            yield {}  # pragma: no cover


class _PsubFailClient:
    """Fake Redis client that pairs with _PsubFailPubSub."""

    def __init__(
        self, phase: int, done: asyncio.Event, real_sleep, fail_until: int
    ) -> None:
        self._phase = phase
        self._done = done
        self._real_sleep = real_sleep
        self._fail_until = fail_until

    def pubsub(self) -> _PsubFailPubSub:
        return _PsubFailPubSub(
            self._phase, self._done, self._real_sleep, self._fail_until
        )

    async def aclose(self) -> None:
        pass


class _MixedPhasePubSub:
    """Fake pub/sub: psubscribe fails in phase 0, listen fails in phase 1, stable in phase 2+."""

    def __init__(self, phase: int, done: asyncio.Event, real_sleep) -> None:
        self._phase = phase
        self._done = done
        self._real_sleep = real_sleep

    async def psubscribe(self, _pattern: str) -> None:
        from redis.exceptions import RedisError

        if self._phase == 0:
            raise RedisError("phase 0: psubscribe fails, delay grows")

    async def aclose(self) -> None:
        pass

    async def listen(self):
        from redis.exceptions import RedisError

        if self._phase == 1:
            raise RedisError("phase 1: listen fails after psubscribe recovery")
        self._done.set()
        while True:
            await self._real_sleep(3600)
            yield {}  # pragma: no cover


class _MixedPhaseClient:
    """Fake Redis client that pairs with _MixedPhasePubSub."""

    def __init__(self, phase: int, done: asyncio.Event, real_sleep) -> None:
        self._phase = phase
        self._done = done
        self._real_sleep = real_sleep

    def pubsub(self) -> _MixedPhasePubSub:
        return _MixedPhasePubSub(self._phase, self._done, self._real_sleep)

    async def aclose(self) -> None:
        pass


class TestRedisListenerBackoff:
    """Exponential backoff and warning logging on repeated Redis connection failures."""

    # ── Pure function tests (no Redis, no async) ──────────────────────────────

    def test_delay_doubles_each_call(self):
        delay = _LISTENER_RECONNECT_DELAY
        assert _next_reconnect_delay(delay) == 2.0
        assert _next_reconnect_delay(2.0) == 4.0
        assert _next_reconnect_delay(4.0) == 8.0

    def test_delay_is_capped_at_cap(self):
        assert _next_reconnect_delay(999.0) == _LISTENER_RECONNECT_CAP_DELAY
        assert (
            _next_reconnect_delay(_LISTENER_RECONNECT_CAP_DELAY)
            == _LISTENER_RECONNECT_CAP_DELAY
        )

    def test_delay_clamps_just_before_cap(self):
        # 16 * 2 = 32, which exceeds the 30s cap
        assert _next_reconnect_delay(16.0) == _LISTENER_RECONNECT_CAP_DELAY

    # ── Integration tests (fake Redis clients) ────────────────────────────────

    @pytest.mark.asyncio
    async def test_warning_logged_on_redis_error(self, sse_module, monkeypatch):
        """A RedisError emits a WARNING before reconnecting."""
        sse = sse_module
        _enable_redis(monkeypatch)
        monkeypatch.setattr(sse, "_LISTENER_RECONNECT_DELAY", 0.0)

        subscribed: list[str] = []
        reconnected = asyncio.Event()
        clients = iter(
            [
                _FlakyClient(fail=True, subscribed=subscribed, reconnected=reconnected),
                _FlakyClient(
                    fail=False, subscribed=subscribed, reconnected=reconnected
                ),
            ]
        )
        monkeypatch.setattr(
            "vibetuner.redis.create_redis_client", lambda: next(clients)
        )

        with patch("vibetuner.sse.logger") as mock_logger:
            await start_redis_listener()
            await asyncio.wait_for(reconnected.wait(), timeout=2)

        mock_logger.warning.assert_called_once()
        warning_call = str(mock_logger.warning.call_args)
        assert "lost connection" in warning_call

    @pytest.mark.asyncio
    async def test_backoff_delay_grows_when_psubscribe_fails(
        self, sse_module, monkeypatch
    ):
        """When psubscribe itself keeps failing (Redis stays down), sleep grows each attempt.

        The delay resets only after psubscribe succeeds, so consecutive psubscribe
        failures accumulate backoff rather than starting over.
        """
        _enable_redis(monkeypatch)
        real_sleep = asyncio.sleep
        sleep_calls: list[float] = []

        async def capturing_sleep(t: float) -> None:
            sleep_calls.append(t)
            await real_sleep(0)

        monkeypatch.setattr(asyncio, "sleep", capturing_sleep)

        done = asyncio.Event()
        call_count = [0]

        def make_client() -> _PsubFailClient:
            n = call_count[0]
            call_count[0] += 1
            return _PsubFailClient(n, done, real_sleep, fail_until=2)

        monkeypatch.setattr("vibetuner.redis.create_redis_client", make_client)

        await start_redis_listener()
        await asyncio.wait_for(done.wait(), timeout=2)

        # Phase 0 psubscribe fails → sleep(1.0) → delay=2.0
        # Phase 1 psubscribe fails → sleep(2.0) → delay=4.0
        # Phase 2 psubscribe succeeds → stable (sets done)
        assert len(sleep_calls) >= 2
        assert sleep_calls[0] == _LISTENER_RECONNECT_DELAY
        assert sleep_calls[1] == _next_reconnect_delay(_LISTENER_RECONNECT_DELAY)
        assert sleep_calls[1] > sleep_calls[0]

    @pytest.mark.asyncio
    async def test_backoff_resets_after_successful_psubscribe(
        self, sse_module, monkeypatch
    ):
        """Once psubscribe succeeds (Redis is back), delay resets so the next failure starts fresh.

        Scenario: psubscribe fails once (delay grows to 2s), then psubscribe succeeds
        but listen drops the connection. The sleep before the third attempt is back
        at base (1s) rather than the accumulated 2s.
        """
        _enable_redis(monkeypatch)
        real_sleep = asyncio.sleep
        sleep_calls: list[float] = []

        async def capturing_sleep(t: float) -> None:
            sleep_calls.append(t)
            await real_sleep(0)

        monkeypatch.setattr(asyncio, "sleep", capturing_sleep)

        done = asyncio.Event()
        call_count = [0]

        def make_client() -> _MixedPhaseClient:
            n = call_count[0]
            call_count[0] += 1
            return _MixedPhaseClient(n, done, real_sleep)

        monkeypatch.setattr("vibetuner.redis.create_redis_client", make_client)

        await start_redis_listener()
        await asyncio.wait_for(done.wait(), timeout=2)

        # Phase 0: psubscribe fails → sleep(1.0) → delay becomes 2.0
        # Phase 1: psubscribe succeeds → delay resets to 1.0 → listen fails → sleep(1.0)
        # Without the reset the second sleep would be 2.0 (accumulated backoff).
        assert len(sleep_calls) >= 2
        assert sleep_calls[0] == _LISTENER_RECONNECT_DELAY
        assert sleep_calls[1] == _LISTENER_RECONNECT_DELAY  # reset, not doubled
