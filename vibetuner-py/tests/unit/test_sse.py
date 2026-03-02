# ABOUTME: Unit tests for SSE event buffer and transport layer
# ABOUTME: Tests ring buffer, event ID assignment, and replay logic
# ruff: noqa: S101

from vibetuner.sse import _EventBuffer, _format_event


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
