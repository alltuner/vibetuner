# ABOUTME: Integration smoke test running a streaq burst worker against a Dockerised Redis.
# ABOUTME: Catches incompatible streaq/coredis pairs and checks worker-start cleanup of stale crons.
# ruff: noqa: S101
import time
from collections.abc import Iterator
from uuid import uuid4

import pytest
import vibetuner.tasks.worker as worker_module
from streaq import Worker
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy
from vibetuner.config import settings
from vibetuner.tasks.lifespan import lifespan


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


@pytest.mark.integration
async def test_worker_start_removes_orphaned_redis_health_check_cron(
    redis_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    worker = Worker(
        redis_url=redis_url,
        redis_kwargs=settings.worker_redis_kwargs,
        queue_name=f"legacy-cron-{uuid4().hex}",
        lifespan=lifespan,
        idle_timeout=settings.worker_idle_timeout,
        handle_signals=False,
    )
    worker.burst = True
    monkeypatch.setattr(worker_module, "worker", worker)

    # Seed the entries streaq 6.0-6.2 persisted for its built-in health check,
    # plus a repeating task this worker does not register, which must survive.
    future_ms = int((time.time() + 3600) * 1000)
    async with worker:
        for name in ("redis_health_check", "nightly_report"):
            await worker.redis.hset(worker.cron_registry_key, {name: "*/5 * * * *"})
            await worker.redis.zadd(worker.cron_schedule_key, {name: future_ms})
            await worker.redis.set(worker.cron_data_key + name, b"payload")

    await worker.run_async()

    async with worker:
        registry = await worker.redis.hgetall(worker.cron_registry_key)
        schedule = await worker.redis.zrange(worker.cron_schedule_key, 0, -1)
        legacy_data = await worker.redis.exists(
            [worker.cron_data_key + "redis_health_check"]
        )
        other_data = await worker.redis.exists(
            [worker.cron_data_key + "nightly_report"]
        )

    assert set(registry) == {"nightly_report"}
    assert list(schedule) == ["nightly_report"]
    assert legacy_data == 0
    assert other_data == 1
