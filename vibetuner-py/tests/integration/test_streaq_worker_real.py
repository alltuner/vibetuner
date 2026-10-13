# ABOUTME: Integration smoke test running a streaq burst worker against a Dockerised Redis.
# ABOUTME: Catches incompatible streaq/coredis pairs and checks worker-start cleanup of stale crons.
# ruff: noqa: S101
import time
from collections.abc import Iterator
from typing import Any
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


def _vibetuner_burst_worker(
    redis_url: str, monkeypatch: pytest.MonkeyPatch
) -> Worker[Any]:
    """Build a burst worker wired to vibetuner's lifespan, as `get_worker()`."""
    worker: Worker[Any] = Worker(
        redis_url=redis_url,
        redis_kwargs=settings.worker_redis_kwargs,
        queue_name=f"cron-cleanup-{uuid4().hex}",
        lifespan=lifespan,
        idle_timeout=settings.worker_idle_timeout,
        handle_signals=False,
    )
    worker.burst = True
    monkeypatch.setattr(worker_module, "worker", worker)
    return worker


async def _seed_cron_entries(worker: Worker[Any], *names: str) -> None:
    """Store cron entries the way streaq persists them, due an hour from now."""
    future_ms = int((time.time() + 3600) * 1000)
    async with worker:
        for name in names:
            await worker.redis.hset(worker.cron_registry_key, {name: "*/5 * * * *"})
            await worker.redis.zadd(worker.cron_schedule_key, {name: future_ms})
            await worker.redis.set(worker.cron_data_key + name, b"payload")


async def _stored_cron_names(worker: Worker[Any], *names: str) -> set[str]:
    """Return which of `names` still have all three cron entries in Redis."""
    stored: set[str] = set()
    async with worker:
        registry = await worker.redis.hgetall(worker.cron_registry_key)
        schedule = set(await worker.redis.zrange(worker.cron_schedule_key, 0, -1))
        for name in names:
            has_data = await worker.redis.exists([worker.cron_data_key + name])
            if name in registry and name in schedule and has_data:
                stored.add(name)
    return stored


@pytest.mark.integration
async def test_worker_start_removes_orphaned_redis_health_check_cron(
    redis_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    worker = _vibetuner_burst_worker(redis_url, monkeypatch)
    # streaq 6.0-6.2 persisted its built-in health check cron like this. The
    # unregistered "nightly_report" stands in for a runtime-scheduled repeating
    # task or another deploy's cron, which must survive.
    await _seed_cron_entries(worker, "redis_health_check", "nightly_report")

    await worker.run_async()

    async with worker:
        registry = await worker.redis.hgetall(worker.cron_registry_key)
        schedule = await worker.redis.zrange(worker.cron_schedule_key, 0, -1)
        health_check_data = await worker.redis.exists(
            [worker.cron_data_key + "redis_health_check"]
        )

    assert set(registry) == {"nightly_report"}
    assert list(schedule) == ["nightly_report"]
    assert health_check_data == 0
    assert await _stored_cron_names(worker, "nightly_report") == {"nightly_report"}


@pytest.mark.integration
async def test_worker_start_keeps_redis_health_check_cron_when_app_registers_it(
    redis_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    worker = _vibetuner_burst_worker(redis_url, monkeypatch)

    @worker.task(name="redis_health_check")
    async def app_health_check() -> None: ...

    await _seed_cron_entries(worker, "redis_health_check")

    await worker.run_async()

    assert await _stored_cron_names(worker, "redis_health_check") == {
        "redis_health_check"
    }
