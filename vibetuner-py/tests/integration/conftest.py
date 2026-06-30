# ABOUTME: Integration-test fixtures that prepare the Docker environment.
# ABOUTME: Resolves the active Docker socket so testcontainers works on Docker Desktop.
import os
from pathlib import Path

import pytest


@pytest.fixture(scope="session", autouse=True)
def docker_host() -> None:
    """Point testcontainers at the active Docker socket.

    docker-py (and therefore testcontainers) defaults to
    ``unix:///var/run/docker.sock``, which Docker Desktop on macOS does not
    create; the daemon listens on the socket named by the current Docker
    context instead. When ``DOCKER_HOST`` is unset and the default socket is
    missing, resolve the context's host and export it so the container fixtures
    can reach the daemon. On Linux/CI, where the default socket exists, this is
    a no-op.
    """
    if os.environ.get("DOCKER_HOST"):
        return
    if Path("/var/run/docker.sock").exists():
        return

    from docker.context import ContextAPI

    host = ContextAPI.get_current_context().Host
    if host:
        os.environ["DOCKER_HOST"] = host
