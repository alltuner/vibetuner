# ABOUTME: Tests for the worker liveness watchdog.
# ABOUTME: Verifies heartbeat refresh and force-exit on a stalled event loop.
"""Tests for the LoopWatchdog."""

# ruff: noqa: S101

import asyncio
import time
from unittest.mock import patch

import pytest
from vibetuner.tasks.watchdog import LoopWatchdog


class TestHeartbeat:
    @pytest.mark.asyncio
    async def test_heartbeat_refreshes_last_beat(self):
        """The heartbeat task advances the recorded beat over time."""
        wd = LoopWatchdog(timeout=10.0, interval=0.01)
        wd._last_beat = time.monotonic() - 100
        wd.start()
        await asyncio.sleep(0.05)
        assert time.monotonic() - wd._last_beat < 1.0
        await wd.stop()


class TestMonitor:
    def test_force_exits_when_loop_stalls(self):
        """A stale heartbeat triggers os._exit(1)."""
        wd = LoopWatchdog(timeout=10.0, interval=0.001)
        wd._last_beat = time.monotonic() - 30  # 30s stale > 10s timeout

        with patch("os._exit", side_effect=lambda _code: wd._stop.set()) as mock_exit:
            wd._monitor()

        mock_exit.assert_called_once_with(1)

    def test_does_not_exit_when_healthy(self):
        """A fresh heartbeat never triggers os._exit."""
        wd = LoopWatchdog(timeout=10.0, interval=0.001)
        wd._last_beat = time.monotonic()
        # Stop after the first wait so the loop runs exactly one iteration.
        wd._stop.set()

        with patch("os._exit") as mock_exit:
            wd._monitor()

        mock_exit.assert_not_called()


class TestLifecycle:
    @pytest.mark.asyncio
    async def test_stop_cancels_heartbeat_task(self):
        """stop() cancels the heartbeat task and stops the thread."""
        wd = LoopWatchdog(timeout=10.0, interval=0.01)
        wd.start()
        thread = wd._thread
        await wd.stop()

        assert wd._task is None
        assert wd._stop.is_set()
        if thread is not None:
            thread.join(timeout=1.0)
            assert not thread.is_alive()
