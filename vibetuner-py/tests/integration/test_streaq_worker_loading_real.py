# ABOUTME: Integration test for a streaq worker starting against a LOADING Redis.
# ABOUTME: Makes a Dockerised Redis read a slow dataset back and starts a worker into it.
# ruff: noqa: S101
import asyncio
import time
from collections.abc import Iterator
from typing import Any
from uuid import uuid4

import pytest
from coredis import Redis
from coredis.exceptions import BusyLoadingError
from streaq import Worker
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy
from vibetuner.config import settings


# Keys to load back, and the microseconds Redis is told to spend on each of
# them, so reading the dataset takes seconds instead of milliseconds.
LOADED_KEYS = 20_000
KEY_LOAD_DELAY_US = 50


@pytest.fixture(scope="module")
def slow_loading_redis(docker_host: None) -> Iterator[DockerContainer]:
    """Redis holding a dataset it reads back slowly, with DEBUG enabled."""
    container = (
        DockerContainer("redis:8")
        .with_exposed_ports(6379)
        .with_command(["redis-server", "--enable-debug-command", "yes"])
        .waiting_for(LogMessageWaitStrategy("Ready to accept connections"))
    )
    with container:
        _redis_cli(container, "debug", "populate", str(LOADED_KEYS))
        _redis_cli(container, "config", "set", "key-load-delay", str(KEY_LOAD_DELAY_US))
        # Redis only answers clients between chunks of the dataset it reads, so
        # a small chunk size is what gets LOADING replies out while it loads.
        _redis_cli(
            container, "config", "set", "loading-process-events-interval-bytes", "1024"
        )
        yield container


def _redis_cli(container: DockerContainer, *args: str) -> str:
    """Run redis-cli inside the container and return its output."""
    exit_code, output = container.exec(["redis-cli", *args])
    assert exit_code == 0, output
    return output.decode()


def _redis_url(container: DockerContainer) -> str:
    host = container.get_container_host_ip()
    return f"redis://{host}:{container.get_exposed_port(6379)}/0"


async def _ping_error(url: str, **redis_kwargs: Any) -> BaseException | None:
    """Return the error a PING raises, or None when Redis answers it."""
    try:
        async with Redis.from_url(url, decode_responses=True, **redis_kwargs) as client:
            await client.ping()
    except BaseException as exc:  # noqa: BLE001
        return exc
    return None


def _is_loading(exc: BaseException | None) -> bool:
    """Whether the error is Redis reporting that it is loading its dataset."""
    if isinstance(exc, BaseExceptionGroup):
        return exc.subgroup(BusyLoadingError) is not None
    return isinstance(exc, BusyLoadingError)


async def _start_loading(container: DockerContainer) -> asyncio.Task[str]:
    """Make Redis reload its dataset and wait until it reports LOADING.

    The returned task holds the blocked DEBUG RELOAD call, which only answers
    once the dataset is back.
    """
    url = _redis_url(container)
    reload = asyncio.create_task(
        asyncio.to_thread(_redis_cli, container, "-t", "60", "debug", "reload")
    )
    deadline = time.monotonic() + 30.0
    while time.monotonic() < deadline:
        if _is_loading(await _ping_error(url)):
            return reload
        await asyncio.sleep(0.05)
    reload.cancel()
    raise AssertionError("Redis never reported LOADING")


@pytest.mark.integration
async def test_default_client_fails_while_redis_is_loading(
    slow_loading_redis: DockerContainer,
) -> None:
    """coredis's own retry handling gives up on a LOADING reply within milliseconds."""
    kwargs = settings.worker_redis_kwargs
    del kwargs["retry_policy"]
    reload = await _start_loading(slow_loading_redis)

    error = await _ping_error(_redis_url(slow_loading_redis), **kwargs)

    assert _is_loading(error)
    await reload


@pytest.mark.integration
async def test_worker_waits_out_redis_loading(
    slow_loading_redis: DockerContainer, log_sink: list[str]
) -> None:
    """A worker starting while Redis loads waits for it and then runs tasks."""
    url = _redis_url(slow_loading_redis)
    worker: Worker[None] = Worker(
        redis_url=url,
        redis_kwargs=settings.worker_redis_kwargs,
        queue_name=f"loading-{uuid4().hex}",
        idle_timeout=settings.worker_idle_timeout,
        handle_signals=False,
    )
    worker.burst = True

    @worker.task
    async def double(value: int) -> int:
        return value * 2

    reload = await _start_loading(slow_loading_redis)

    async with worker:
        queued = await double.enqueue(21)
    await worker.run_async()
    async with worker:
        result = await queued.result(timeout=5)

    assert result.success
    assert result.result == 42
    assert any("loading its dataset" in message for message in log_sink)
    await reload
