# ABOUTME: Liveness watchdog that force-exits a worker whose event loop stalls.
# ABOUTME: A daemon thread restarts the process when the loop stops ticking.
import asyncio
import os
import threading
import time

from vibetuner.logging import logger


class LoopWatchdog:
    """Force-exit the process if the asyncio event loop stops ticking.

    A daemon thread, independent of the loop, watches a heartbeat that an
    asyncio task refreshes every ``interval`` seconds. If the loop wedges (for
    example on a blocking call that never returns), the heartbeat goes stale
    and the thread force-exits so a ``restart`` policy can recover the worker.
    """

    def __init__(self, timeout: float, interval: float) -> None:
        self._timeout = timeout
        self._interval = interval
        self._last_beat = time.monotonic()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._task: asyncio.Task[None] | None = None

    async def _heartbeat(self) -> None:
        while True:
            self._last_beat = time.monotonic()
            await asyncio.sleep(self._interval)

    def _monitor(self) -> None:
        while not self._stop.wait(self._interval):
            stalled = time.monotonic() - self._last_beat
            if stalled > self._timeout:
                logger.critical(
                    "Worker event loop stalled for {:.0f}s (>{:.0f}s); "
                    "force-exiting so the process is restarted",
                    stalled,
                    self._timeout,
                )
                os._exit(1)

    def start(self) -> None:
        """Start the heartbeat task and the monitoring thread."""
        self._last_beat = time.monotonic()
        self._task = asyncio.create_task(self._heartbeat())
        self._thread = threading.Thread(
            target=self._monitor, name="loop-watchdog", daemon=True
        )
        self._thread.start()
        logger.debug(
            "Loop watchdog started (timeout={}s, interval={}s)",
            self._timeout,
            self._interval,
        )

    async def stop(self) -> None:
        """Stop the monitoring thread and cancel the heartbeat task."""
        self._stop.set()
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
