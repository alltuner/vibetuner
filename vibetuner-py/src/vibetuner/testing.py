# ABOUTME: Pytest fixtures and testing utilities for vibetuner applications.
# ABOUTME: Provides test client, mock auth, mock DB, mock tasks, and config overrides.
import os
import uuid
from typing import Any, AsyncGenerator, Iterator
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from starlette.authentication import AuthCredentials

from vibetuner.frontend.oauth import WebUser
from vibetuner.logging import logger
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


async def _truncate_collections(database: AsyncDatabase) -> None:
    """Delete every document from every non-system collection."""
    for name in await database.list_collection_names():
        if name.startswith("system."):
            continue
        await database[name].delete_many({})


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def _vibetuner_db_session() -> AsyncGenerator[str, None]:
    """Session-scoped MongoDB test database with indexes built once.

    Creates a uniquely-named database (namespaced per ``pytest-xdist``
    worker so parallel runs don't collide), runs ``init_beanie`` with
    full index registration once for the entire session, yields the DB
    name, and drops the database on session teardown.

    The ``AsyncMongoClient`` used here lives only on the session event
    loop; per-test fixtures create their own function-loop clients and
    re-wire Beanie via ``init_beanie(skip_indexes=True)``. Sharing the
    client across loops is impossible (pymongo binds it on first use),
    so the only thing shared across tests is the database itself
    (collections + indexes living server-side).

    The throwaway database is created on ``TEST_MONGODB_URL`` when set,
    otherwise on ``MONGODB_URL``. Pointing ``TEST_MONGODB_URL`` at a local
    Mongo keeps the suite off a prod-pointing ``MONGODB_URL``. The resolved
    server and database name are logged at session start so it is obvious
    where the throwaway database lives.

    Skips the session if neither ``TEST_MONGODB_URL`` nor ``MONGODB_URL`` is
    set.
    """
    from beanie import init_beanie

    from vibetuner.config import settings
    from vibetuner.mongo import _mongo_endpoint, get_all_models

    test_url = settings.resolved_test_mongodb_url
    if test_url is None:
        pytest.skip("MongoDB not configured (set TEST_MONGODB_URL or MONGODB_URL)")

    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "main")
    test_db_name = f"test_{worker_id}_{uuid.uuid4().hex[:8]}"

    logger.info(
        "Test MongoDB session: creating throwaway database {!r} on {}",
        test_db_name,
        _mongo_endpoint(test_url),
    )

    # Redirect every consumer of ``settings.mongodb_url`` (framework code via
    # ``_ensure_client``, user code) and ``settings.mongo_dbname`` at the test
    # server + throwaway database for the whole run.
    original_url = settings.mongodb_url
    settings.mongodb_url = test_url
    original = type(settings).mongo_dbname
    type(settings).mongo_dbname = property(lambda self: test_db_name)  # type: ignore[assignment]  # ty: ignore[invalid-assignment]
    settings.__dict__.pop("mongo_dbname", None)

    session_client: AsyncMongoClient = AsyncMongoClient(
        host=str(test_url),
        compressors=["zstd"],
    )
    try:
        await init_beanie(
            database=session_client[test_db_name],
            document_models=get_all_models(),
        )
        yield test_db_name
    finally:
        try:
            await session_client.drop_database(test_db_name)
        finally:
            await session_client.close()
            settings.mongodb_url = original_url
            type(settings).mongo_dbname = original  # type: ignore[assignment]
            settings.__dict__.pop("mongo_dbname", None)


@pytest_asyncio.fixture
async def vibetuner_db(_vibetuner_db_session: str) -> AsyncGenerator[str, None]:
    """MongoDB test database wired to the current event loop with clean
    collections.

    Backed by a session-scoped database whose indexes are built once
    (see ``_vibetuner_db_session``). Each test creates its own
    ``AsyncMongoClient`` on the function event loop, wires Beanie to
    that client with ``skip_indexes=True`` (the indexes already exist
    on the shared DB), and truncates every non-system collection both
    before and after the test. Truncating twice makes the fixture
    self-healing if a previous test crashed before its own teardown
    ran.

    Skips the test if ``MONGODB_URL`` is not set.

    Caveats:
        - All tests in a session share the same database. Tests must not
          assert on database-level state (existence, name, full collection
          drops) or on indexes being absent.
        - Concurrent runs need ``pytest-xdist``; the session DB name
          includes the worker id so each worker is isolated.
    """
    from beanie import init_beanie

    import vibetuner.mongo as mongo_mod
    from vibetuner.mongo import _ensure_client, get_all_models, teardown_mongodb

    test_db_name = _vibetuner_db_session

    _ensure_client()
    if mongo_mod.mongo_client is None:
        pytest.skip("MongoDB not configured (MONGODB_URL not set)")

    database = mongo_mod.mongo_client[test_db_name]
    await init_beanie(
        database=database,
        document_models=get_all_models(),
        skip_indexes=True,
    )
    await _truncate_collections(database)

    try:
        yield test_db_name
    finally:
        try:
            await _truncate_collections(database)
        finally:
            await teardown_mongodb()


# ---------------------------------------------------------------------------
# Redis test server
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture(scope="session", loop_scope="session", autouse=True)
async def _vibetuner_redis_session() -> AsyncGenerator[None, None]:
    """Point every Redis consumer at the test Redis for the whole session.

    Overrides ``settings.redis_url`` with ``resolved_test_redis_url`` so the
    rate limiter, response cache, pub/sub, and the shared Redis client all
    target ``TEST_REDIS_URL`` when set. Falling back to ``redis_url`` when
    ``TEST_REDIS_URL`` is unset keeps existing behavior unchanged, exactly as
    ``TEST_MONGODB_URL`` does for Mongo.

    Pointing ``TEST_REDIS_URL`` at a local Redis keeps the suite off a
    prod-pointing ``redis_url`` so requests through ``vibetuner_client`` don't
    pay remote round-trip latency on every rate-limit and cache lookup.
    """
    from vibetuner.config import settings
    from vibetuner.redis import close_redis_client

    original_url = settings.redis_url
    settings.redis_url = settings.resolved_test_redis_url
    await close_redis_client()
    try:
        yield
    finally:
        await close_redis_client()
        settings.redis_url = original_url


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
def mock_auth() -> Iterator[MockAuth]:
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
