# ABOUTME: Pytest fixtures and testing utilities for vibetuner applications.
# ABOUTME: Provides test client, mock auth, mock DB, mock tasks, and config overrides.
from __future__ import annotations

import uuid
from typing import Any, AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from starlette.authentication import AuthCredentials

from vibetuner.frontend.oauth import WebUser
from vibetuner.runtime_config import RuntimeConfig


# ---------------------------------------------------------------------------
# Test client
# ---------------------------------------------------------------------------


@pytest.fixture
def vibetuner_app() -> FastAPI:
    """Return the default vibetuner FastAPI application.

    Override this fixture in your ``conftest.py`` to supply a custom app
    instance (e.g., one with extra test routes).
    """
    from vibetuner.frontend import app

    return app


@pytest_asyncio.fixture
async def vibetuner_client(
    vibetuner_app: FastAPI,
) -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP test client with the full vibetuner app (middleware included).

    Uses ``httpx.AsyncClient`` with ``ASGITransport`` so that middleware,
    authentication, sessions, and HTMX headers all work as in production.

    Override the ``vibetuner_app`` fixture to supply a custom app.
    """
    transport = ASGITransport(app=vibetuner_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# ---------------------------------------------------------------------------
# MongoDB test database
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def vibetuner_db() -> AsyncGenerator[str, None]:
    """Temporary MongoDB test database with Beanie initialised.

    Creates a uniquely-named database, initialises Beanie with all
    registered models, yields the DB name, and drops the database on
    teardown. Skips the test if ``MONGODB_URL`` is not set.
    """
    import vibetuner.mongo as mongo_mod
    from vibetuner.config import settings
    from vibetuner.mongo import _ensure_client, get_all_models

    test_db_name = f"test_{uuid.uuid4().hex[:12]}"

    _ensure_client()
    if mongo_mod.mongo_client is None:
        pytest.skip("MongoDB not configured (MONGODB_URL not set)")

    # Override the DB name used by all framework code
    original = type(settings).mongo_dbname
    type(settings).mongo_dbname = property(lambda self: test_db_name)  # type: ignore[assignment]
    settings.__dict__.pop("mongo_dbname", None)

    try:
        from beanie import init_beanie

        await init_beanie(
            database=mongo_mod.mongo_client[test_db_name],
            document_models=get_all_models(),
        )
        yield test_db_name
    finally:
        if mongo_mod.mongo_client is not None:
            await mongo_mod.mongo_client.drop_database(test_db_name)
        type(settings).mongo_dbname = original  # type: ignore[assignment]
        settings.__dict__.pop("mongo_dbname", None)


# ---------------------------------------------------------------------------
# Authentication mocking
# ---------------------------------------------------------------------------


class MockAuth:
    """Controls the authentication state seen by the test client.

    When used as a fixture, it patches ``AuthBackend.authenticate`` so that
    requests through ``vibetuner_client`` see the mocked user without
    requiring real sessions or cookies.
    """

    def __init__(self) -> None:
        self._user: WebUser | None = None

    def login(
        self,
        *,
        user_id: str | None = None,
        name: str = "Test User",
        email: str = "test@example.com",
        picture: str | None = None,
    ) -> WebUser:
        """Set the current request user to an authenticated state."""
        uid = user_id or str(uuid.uuid4())
        self._user = WebUser(id=uid, name=name, email=email, picture=picture)
        return self._user

    def logout(self) -> None:
        """Clear the current user (requests will be unauthenticated)."""
        self._user = None

    @property
    def user(self) -> WebUser | None:
        return self._user

    async def _authenticate(self, conn):
        if self._user is not None:
            return AuthCredentials(["authenticated"]), self._user
        return None


@pytest.fixture
def mock_auth() -> MockAuth:
    """Fixture for mocking authentication in tests.

    Patches the Starlette ``AuthBackend`` used by vibetuner so that
    calling ``mock_auth.login(...)`` makes subsequent requests appear
    authenticated — no session cookies needed.

    Usage::

        async def test_profile(vibetuner_client, mock_auth):
            mock_auth.login(name="Alice", email="alice@example.com")
            resp = await vibetuner_client.get("/user/profile")
            assert resp.status_code == 200

            mock_auth.logout()
            resp = await vibetuner_client.get("/user/profile")
            assert resp.status_code != 200
    """
    ctx = MockAuth()
    with patch(
        "vibetuner.frontend.middleware.AuthBackend.authenticate",
        side_effect=ctx._authenticate,
    ):
        yield ctx  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Background-task mocking (no Redis required)
# ---------------------------------------------------------------------------


class MockTaskResult:
    """Minimal stand-in for a Streaq task result."""

    def __init__(self, result: Any = None) -> None:
        self.result = result
        self.success = True
        self.exception = None


class MockTask:
    """Records ``enqueue`` calls for a single task function.

    Use with ``unittest.mock.patch`` to replace a real task::

        with patch("myapp.tasks.emails.send_welcome", mock_tasks.send_welcome):
            ...
        assert mock_tasks.send_welcome.enqueue.called
    """

    def __init__(self) -> None:
        self.calls: list[tuple[tuple, dict]] = []
        self.enqueue = AsyncMock(side_effect=self._record)

    async def _record(self, *args: Any, **kwargs: Any) -> MockTaskResult:
        self.calls.append((args, kwargs))
        return MockTaskResult()


class MockTasks:
    """Auto-vivifying registry of :class:`MockTask` instances.

    Attribute access creates a new mock on first use, so you can write
    ``mock_tasks.any_task_name`` without prior setup.
    """

    def __init__(self) -> None:
        self._tasks: dict[str, MockTask] = {}

    def __getattr__(self, name: str) -> MockTask:
        if name.startswith("_"):
            raise AttributeError(name)
        if name not in self._tasks:
            self._tasks[name] = MockTask()
        return self._tasks[name]

    def reset(self) -> None:
        """Clear all recorded calls."""
        for task in self._tasks.values():
            task.calls.clear()
            task.enqueue.reset_mock()


@pytest.fixture
def mock_tasks() -> MockTasks:
    """Mock background tasks without requiring Redis.

    Usage::

        async def test_signup(vibetuner_client, mock_tasks):
            with patch(
                "myapp.tasks.emails.send_welcome_email",
                mock_tasks.send_welcome_email,
            ):
                resp = await vibetuner_client.post("/signup", data={...})
            assert mock_tasks.send_welcome_email.enqueue.called
    """
    return MockTasks()


# ---------------------------------------------------------------------------
# Runtime config overrides
# ---------------------------------------------------------------------------


class ConfigOverrider:
    """Async-callable that sets ``RuntimeConfig`` overrides and tracks them
    for automatic cleanup.
    """

    def __init__(self) -> None:
        self._keys: list[str] = []

    async def __call__(self, key: str, value: Any) -> None:
        await RuntimeConfig.set_runtime_override(key, value)
        self._keys.append(key)

    async def _cleanup(self) -> None:
        for key in self._keys:
            await RuntimeConfig.clear_runtime_override(key)
        self._keys.clear()


@pytest_asyncio.fixture
async def override_config() -> AsyncGenerator[ConfigOverrider, None]:
    """Override ``RuntimeConfig`` values for a single test.

    All overrides are automatically removed when the test ends.

    Usage::

        async def test_feature_flag(override_config):
            await override_config("features.dark_mode", True)
            value = await RuntimeConfig.get("features.dark_mode")
            assert value is True
    """
    overrider = ConfigOverrider()
    yield overrider
    await overrider._cleanup()
