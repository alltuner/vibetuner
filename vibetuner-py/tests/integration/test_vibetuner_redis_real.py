# ABOUTME: Integration test for the shared Redis client's lifecycle across tests.
# ABOUTME: Runs an inner pytest session against a Dockerised Redis and checks it ends cleanly.
from collections.abc import Iterator

import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy


pytest_plugins = ["pytester"]


@pytest.fixture(scope="module")
def redis_url(docker_host: None) -> Iterator[str]:
    container = (
        DockerContainer("redis:8-alpine")
        .with_exposed_ports(6379)
        .waiting_for(LogMessageWaitStrategy("Ready to accept connections"))
    )
    with container:
        host = container.get_container_host_ip()
        port = container.get_exposed_port(6379)
        yield f"redis://{host}:{port}/0"


_INNER_TEST = """
@pytest.mark.asyncio
async def test_uses_redis_{n}():
    client = await get_redis_client()
    assert await client.ping()
"""


@pytest.mark.integration
@pytest.mark.parametrize("test_count", [1, 2])
def test_tests_that_use_the_shared_client_finish_cleanly(
    pytester: pytest.Pytester,
    monkeypatch: pytest.MonkeyPatch,
    redis_url: str,
    test_count: int,
) -> None:
    """Each test's event loop is closed when the test ends, so a shared client
    created inside a test must not outlive it: reusing it in the next test or
    closing it at session teardown would touch a closed loop.
    """
    monkeypatch.setenv("REDIS_URL", redis_url)
    pytester.makepyfile(
        "import pytest\n"
        "from vibetuner.redis import get_redis_client\n"
        + "".join(_INNER_TEST.format(n=n) for n in range(test_count))
    )

    result = pytester.runpytest_subprocess("-p", "no:cacheprovider")

    result.assert_outcomes(passed=test_count)
