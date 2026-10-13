# ABOUTME: Integration smoke test running a streaq burst worker against a Dockerised Redis.
# ABOUTME: Catches incompatible streaq/coredis pairs that crash the worker on the first task.
# ruff: noqa: S101
from collections.abc import Iterator
from uuid import uuid4

import pytest
from streaq import Worker
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy
from vibetuner.config import settings


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


@pytest.mark.integration
async def test_burst_worker_runs_a_queued_task(redis_url: str) -> None:
    worker = Worker(
        redis_url=redis_url,
        redis_kwargs=settings.worker_redis_kwargs,
        queue_name=f"smoke-{uuid4().hex}",
        idle_timeout=settings.worker_idle_timeout,
        handle_signals=False,
    )
    worker.burst = True

    @worker.task
    async def double(value: int) -> int:
        return value * 2

    async with worker:
        queued = await double.enqueue(21)

    await worker.run_async()

    async with worker:
        result = await queued.result(timeout=5)

    assert result.success
    assert result.result == 42
