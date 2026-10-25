# ABOUTME: Integration tests for streaq's versioned Lua names against a Dockerised Redis.
# ABOUTME: A worker must load streaq_v7 and keep working next to another project's unversioned library.
# ruff: noqa: S101
from collections.abc import AsyncGenerator, Iterator
from contextlib import asynccontextmanager
from typing import Any
from uuid import uuid4

import coredis
import pytest
import vibetuner.tasks.worker  # noqa: F401  (applies the versioned names)
from anyio import create_task_group, fail_after
from streaq import Worker
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy
from vibetuner.config import settings


# What another project's streaq <= 7.2 loads into the same server: the
# unversioned library, here with functions that fail loudly, so a worker that
# still calls the unversioned names errors instead of hanging.
UNVERSIONED_STUB_LIBRARY = """#!lua name=streaq

redis.register_function('publish_task', function(keys, argv)
  return redis.error_reply('unversioned publish_task called')
end)

redis.register_function('publish_delayed_tasks', function(keys, argv)
  return redis.error_reply('unversioned publish_delayed_tasks called')
end)
"""


@pytest.fixture(scope="module")
def redis_url(docker_host: None) -> Iterator[str]:
    """Spin up a Redis container of this module's own, since it flushes functions."""
    container = (
        DockerContainer("redis:8")
        .with_exposed_ports(6379)
        .waiting_for(LogMessageWaitStrategy("Ready to accept connections"))
    )
    with container:
        host = container.get_container_host_ip()
        port = container.get_exposed_port(6379)
        yield f"redis://{host}:{port}/0"


@asynccontextmanager
async def _client(redis_url: str) -> "AsyncGenerator[coredis.Redis[str], None]":
    async with coredis.Redis.from_url(redis_url, decode_responses=True) as conn:
        yield conn


async def _load_unversioned_stub(redis_url: str) -> None:
    async with _client(redis_url) as client:
        await client.function_load(UNVERSIONED_STUB_LIBRARY, replace=True)


async def _libraries(redis_url: str) -> dict[str, set[str]]:
    async with _client(redis_url) as client:
        libraries = await client.function_list()
    return {name: set(lib["functions"]) for name, lib in libraries.items()}


def _worker(redis_url: str) -> Worker[Any]:
    """Build a worker configured as vibetuner's own, on a queue of its own."""
    return Worker(
        redis_url=redis_url,
        redis_kwargs=settings.worker_redis_kwargs,
        queue_name=f"versioned-{uuid4().hex}",
        idle_timeout=settings.worker_idle_timeout,
        handle_signals=False,
    )


@pytest.fixture
async def flushed(redis_url: str) -> str:
    async with _client(redis_url) as client:
        await client.function_flush()
    return redis_url


@pytest.mark.integration
async def test_worker_loads_the_versioned_library(flushed: str) -> None:
    async with _worker(flushed):
        libraries = await _libraries(flushed)

    assert set(libraries) == {"streaq_v7"}
    functions = libraries["streaq_v7"]
    assert functions
    assert all(name.startswith("streaq_v7_") for name in functions)


@pytest.mark.integration
@pytest.mark.parametrize("stub_loaded", ["before_start", "after_start"])
async def test_tasks_run_next_to_an_unversioned_library(
    flushed: str, stub_loaded: str
) -> None:
    worker = _worker(flushed)

    @worker.task
    async def double(value: int) -> int:
        return value * 2

    if stub_loaded == "before_start":
        await _load_unversioned_stub(flushed)

    with fail_after(15):
        async with create_task_group() as tg:
            await tg.start(worker.run_async)
            if stub_loaded == "after_start":
                await _load_unversioned_stub(flushed)

            immediate = await double.enqueue(21)
            dependent = await double.enqueue(1).start(after=immediate.id)
            delayed = await double.enqueue(4).start(delay=1)
            immediate_result = await immediate.result(timeout=10)
            dependent_result = await dependent.result(timeout=10)
            delayed_result = await delayed.result(timeout=10)
            tg.cancel_scope.cancel()

    assert immediate_result.success, immediate_result.exception
    assert immediate_result.result == 42
    assert dependent_result.success, dependent_result.exception
    assert dependent_result.result == 2
    assert delayed_result.success, delayed_result.exception
    assert delayed_result.result == 8
    libraries = await _libraries(flushed)
    assert libraries["streaq"] == {"publish_task", "publish_delayed_tasks"}
    assert "streaq_v7" in libraries
