# ABOUTME: Integration tests for the worker-health probe against real streaq workers and Redis.
# ABOUTME: Proves the probe finds live workers by id without scanning the keyspace.
# ruff: noqa: S101
import asyncio
from collections.abc import AsyncIterator, Iterator
from datetime import timedelta
from uuid import uuid4

import pytest
import redis.asyncio as aioredis
from streaq import Worker
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy
from vibetuner.cli.health import has_live_worker
from vibetuner.config import settings


IDLE_TIMEOUT = timedelta(seconds=2)
UNRELATED_KEYS = 200_000


@pytest.fixture(scope="module")
def redis_url(docker_host: None) -> Iterator[str]:
    """Spin up a Redis container and yield its connection URL."""
    container = (
        DockerContainer("redis:8")
        .with_exposed_ports(6379)
        .waiting_for(LogMessageWaitStrategy("Ready to accept connections"))
    )
    with container:
        host = container.get_container_host_ip()
        port = container.get_exposed_port(6379)
        yield f"redis://{host}:{port}/0"


@pytest.fixture
async def client(redis_url: str) -> AsyncIterator[aioredis.Redis]:
    client = aioredis.from_url(redis_url)
    yield client
    await client.aclose()


@pytest.fixture
def queue_name() -> str:
    return f"health-{uuid4().hex}"


class RunningWorker:
    """A real streaq worker running in the background until stopped."""

    def __init__(self, redis_url: str, queue_name: str) -> None:
        self.worker: Worker[None] = Worker(
            redis_url=redis_url,
            redis_kwargs=settings.worker_redis_kwargs,
            queue_name=queue_name,
            idle_timeout=IDLE_TIMEOUT,
            handle_signals=False,
        )
        self._task = asyncio.create_task(self.worker.run_async())

    async def stop(self) -> None:
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass


async def _wait_for(
    client: aioredis.Redis, queue_name: str, expected: bool, timeout: float = 10
) -> bool:
    """Poll the probe until it reports ``expected`` or the timeout passes."""
    deadline = asyncio.get_running_loop().time() + timeout
    while True:
        result = await has_live_worker(client, queue_name)
        if result is expected or asyncio.get_running_loop().time() > deadline:
            return result
        await asyncio.sleep(0.1)


@pytest.mark.integration
async def test_no_worker_ever_started_is_unhealthy(
    client: aioredis.Redis, queue_name: str
) -> None:
    assert await has_live_worker(client, queue_name) is False


@pytest.mark.integration
async def test_live_worker_is_found_without_scanning(
    redis_url: str, client: aioredis.Redis, queue_name: str
) -> None:
    for start in range(0, UNRELATED_KEYS, 10_000):
        await client.mset({f"otherapp:{i}": "x" for i in range(start, start + 10_000)})

    worker = RunningWorker(redis_url, queue_name)
    try:
        assert await _wait_for(client, queue_name, expected=True) is True

        await client.config_resetstat()
        assert await has_live_worker(client, queue_name) is True
        stats = await client.info("commandstats")
        assert "cmdstat_scan" not in stats
        assert "cmdstat_keys" not in stats
    finally:
        await worker.stop()


@pytest.mark.integration
async def test_stopped_worker_expires_to_unhealthy(
    redis_url: str, client: aioredis.Redis, queue_name: str
) -> None:
    worker = RunningWorker(redis_url, queue_name)
    assert await _wait_for(client, queue_name, expected=True) is True
    await worker.stop()

    assert await _wait_for(client, queue_name, expected=False) is False


@pytest.mark.integration
async def test_restarted_worker_with_new_id_is_healthy(
    redis_url: str, client: aioredis.Redis, queue_name: str
) -> None:
    first = RunningWorker(redis_url, queue_name)
    assert await _wait_for(client, queue_name, expected=True) is True
    await first.stop()
    assert await _wait_for(client, queue_name, expected=False) is False

    second = RunningWorker(redis_url, queue_name)
    try:
        assert second.worker.id != first.worker.id
        assert await _wait_for(client, queue_name, expected=True) is True
    finally:
        await second.stop()


@pytest.mark.integration
async def test_surviving_replica_keeps_queue_healthy(
    redis_url: str, client: aioredis.Redis, queue_name: str
) -> None:
    replica_a = RunningWorker(redis_url, queue_name)
    replica_b = RunningWorker(redis_url, queue_name)
    try:
        assert await _wait_for(client, queue_name, expected=True) is True
        await replica_a.stop()
        # Outlast replica A's health key so only replica B can satisfy the probe.
        await asyncio.sleep(IDLE_TIMEOUT.total_seconds() * 2)
        assert await has_live_worker(client, queue_name) is True
    finally:
        await replica_b.stop()
