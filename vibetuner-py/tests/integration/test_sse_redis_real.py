# ABOUTME: Integration test for SSE publishing through the shared Redis client.
# ABOUTME: Checks broadcasts follow the shared client when it is recreated against another Redis.
# ruff: noqa: S101
import json
from collections.abc import AsyncIterator, Iterator
from contextlib import ExitStack, asynccontextmanager
from typing import Any

import pytest
import redis.asyncio as aioredis
from redis.asyncio.client import PubSub
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy
from vibetuner.config import settings
from vibetuner.redis import close_redis_client
from vibetuner.sse import broadcast


def _redis_container() -> DockerContainer:
    return (
        DockerContainer("redis:8-alpine")
        .with_exposed_ports(6379)
        .waiting_for(LogMessageWaitStrategy("Ready to accept connections"))
    )


@pytest.fixture(scope="module")
def redis_urls(docker_host: None) -> Iterator[tuple[str, str]]:
    """Spin up two independent Redis servers and yield their URLs."""
    with ExitStack() as stack:
        urls = [
            f"redis://{c.get_container_host_ip()}:{c.get_exposed_port(6379)}/0"
            for c in (stack.enter_context(_redis_container()) for _ in range(2))
        ]
        yield urls[0], urls[1]


@asynccontextmanager
async def _subscribed(url: str, channel: str) -> AsyncIterator[PubSub]:
    client = aioredis.from_url(url)
    pubsub = client.pubsub()
    try:
        await pubsub.subscribe(f"{settings.redis_key_prefix}sse:{channel}")
        assert await pubsub.get_message(timeout=5) is not None
        yield pubsub
    finally:
        await pubsub.aclose()
        await client.aclose()


async def _next_payload(pubsub: PubSub) -> dict[str, Any] | None:
    message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=5)
    return None if message is None else json.loads(message["data"])


@pytest.mark.integration
async def test_broadcast_publishes_through_recreated_shared_client(
    redis_urls: tuple[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    first_url, second_url = redis_urls

    monkeypatch.setattr(settings, "redis_url", first_url)
    await close_redis_client()
    async with _subscribed(first_url, "room") as pubsub:
        await broadcast("room", "update", data="first")
        first = await _next_payload(pubsub)

    monkeypatch.setattr(settings, "redis_url", second_url)
    await close_redis_client()
    async with _subscribed(second_url, "room") as pubsub:
        await broadcast("room", "update", data="second")
        second = await _next_payload(pubsub)
    await close_redis_client()

    assert first is not None
    assert first["data"] == "first"
    assert second is not None
    assert second["data"] == "second"
