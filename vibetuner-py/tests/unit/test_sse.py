# ABOUTME: Unit tests for SSE event buffer and transport layer
# ABOUTME: Tests ring buffer, event ID assignment, replay logic, and channel streaming resumption
# ruff: noqa: S101

import asyncio

import pytest
from vibetuner.sse import (
    _channel_buffers,
    _dispatch_local,
    _EventBuffer,
    _format_event,
    _stream_from_channel,
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
            items = await asyncio.wait_for(
                self._collect_n(gen, 2), timeout=2.0
            )
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
