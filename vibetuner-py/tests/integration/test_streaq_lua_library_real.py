# ABOUTME: Integration tests for the streaq Lua library probe against a Dockerised Redis.
# ABOUTME: A library left by a different streaq version must be detected, not silently tolerated.
# ruff: noqa: S101
import inspect
import time
from collections.abc import AsyncGenerator, Iterator
from contextlib import asynccontextmanager
from pathlib import Path

import coredis
import pytest
import streaq
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy
from vibetuner.tasks.lua_library import promotes_delayed_tasks


# A stand-in for the library streaq <= 7.1.0 installs: same library and function
# names, but the pre-7.2 calling convention, where keys[1] is a prefix and the
# priorities arrive in argv. Called the 7.2 way it promotes nothing and still
# reports success, which is the silent failure this probe exists to catch.
OLD_CONVENTION_LIBRARY = """#!lua name=streaq

redis.register_function('publish_delayed_tasks', function(keys, argv)
  local queue_key = keys[1]
  local stream_key = keys[2]
  local current_time = argv[1]

  for i = 2, #argv do
    local queue = queue_key .. argv[i]
    local tids = redis.call('zrange', queue, 0, current_time, 'byscore', 'withscores')
    if #tids > 0 then
      redis.call('zremrangebyscore', queue, 0, current_time)
      for j = 1, #tids, 2 do
        redis.call('xadd', stream_key, '*', 'task_id', tids[j])
      end
    end
  end
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


def _shipped_library() -> str:
    return (Path(inspect.getfile(streaq)).parent / "lua" / "streaq.lua").read_text()


@asynccontextmanager
async def _client(redis_url: str) -> "AsyncGenerator[coredis.Redis[str], None]":
    """Open a coredis client for one test.

    Entering and exiting coredis' pool inside the test body keeps both in the
    same task, which an async fixture would not guarantee.
    """
    async with coredis.Redis.from_url(redis_url, decode_responses=True) as conn:
        yield conn


async def _load_library(client: "coredis.Redis[str]", code: str) -> None:
    await client.function_flush()
    await client.function_load(code, replace=True)


@pytest.mark.integration
class TestLuaLibraryProbe:
    async def test_passes_with_the_shipped_library(self, redis_url: str) -> None:
        async with _client(redis_url) as client:
            await _load_library(client, _shipped_library())

            assert await promotes_delayed_tasks(client, "probe-ok:") is True

    async def test_fails_when_an_older_library_owns_the_functions(
        self, redis_url: str
    ) -> None:
        async with _client(redis_url) as client:
            await _load_library(client, OLD_CONVENTION_LIBRARY)

            assert await promotes_delayed_tasks(client, "probe-old:") is False

    async def test_fails_when_no_library_is_installed(self, redis_url: str) -> None:
        async with _client(redis_url) as client:
            await client.function_flush()

            assert await promotes_delayed_tasks(client, "probe-missing:") is False

    async def test_leaves_no_keys_behind(self, redis_url: str) -> None:
        async with _client(redis_url) as client:
            await _load_library(client, _shipped_library())

            await promotes_delayed_tasks(client, "probe-clean:")

            assert await client.keys("probe-clean:*") == set()

    async def test_leaves_the_real_queues_alone(self, redis_url: str) -> None:
        async with _client(redis_url) as client:
            await _load_library(client, _shipped_library())
            queue = "streaq:realproject:queues:delayed:normal"
            stream = "streaq:realproject:queues:normal"
            due = int(time.time() * 1000) - 1000
            await client.zadd(queue, {"real-task": due})

            await promotes_delayed_tasks(client, "realproject:")

            assert await client.zcard(queue) == 1
            assert await client.exists([stream]) == 0
