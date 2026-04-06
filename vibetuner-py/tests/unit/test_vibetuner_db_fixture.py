# ABOUTME: Tests that the vibetuner_db fixture resets the MongoDB client on teardown.
# ABOUTME: Prevents AsyncMongoClient from leaking across event loops in test runs.
# ruff: noqa: S101
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import vibetuner.mongo as mongo_mod


async def _run_fixture_lifecycle():
    """Run the vibetuner_db generator logic directly (bypassing pytest decorator).

    Duplicates the fixture body so the test doesn't depend on pytest fixture
    internals, while still exercising the exact same teardown path.
    """
    # Import the same things the fixture does
    from vibetuner.testing import vibetuner_db

    # Access the raw coroutine under the pytest_asyncio wrapper
    gen = vibetuner_db.__wrapped__()
    db_name = await gen.__anext__()

    # Simulate teardown
    with pytest.raises(StopAsyncIteration):
        await gen.__anext__()

    return db_name


@pytest.mark.unit
class TestVibetunerDbFixtureCleanup:
    """The vibetuner_db fixture must reset mongo_client on teardown.

    When pytest-asyncio uses function-scoped event loops (the default),
    each test gets a new loop. AsyncMongoClient binds to the loop it was
    created on, so a stale client causes RuntimeError in the next test.
    The fixture must close and reset the client during teardown.
    """

    async def test_mongo_client_is_none_after_teardown(self):
        """After vibetuner_db yields and tears down, mongo_client must be None."""
        mock_client = MagicMock()
        mock_client.__getitem__ = MagicMock(return_value=MagicMock())
        mock_client.drop_database = AsyncMock()
        mock_client.close = AsyncMock()

        with (
            patch.object(mongo_mod, "mongo_client", None),
            patch(
                "vibetuner.mongo._ensure_client",
                side_effect=lambda: setattr(mongo_mod, "mongo_client", mock_client),
            ),
            patch("vibetuner.config.settings") as mock_settings,
            patch("beanie.init_beanie", new_callable=AsyncMock),
            patch("vibetuner.mongo.get_all_models", return_value=[]),
        ):
            mock_settings.mongodb_url = "mongodb://localhost:27017"
            type(mock_settings).mongo_dbname = property(lambda self: "original_db")

            db_name = await _run_fixture_lifecycle()
            assert db_name.startswith("test_")

            # The client must have been closed and reset
            mock_client.close.assert_awaited_once()
            assert mongo_mod.mongo_client is None
