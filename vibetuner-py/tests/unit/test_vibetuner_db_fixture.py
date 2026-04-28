# ABOUTME: Tests that the per-test vibetuner_db fixture wires Beanie with
# ABOUTME: skip_indexes, truncates collections, and resets the client on teardown.
# ruff: noqa: S101
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import vibetuner.mongo as mongo_mod


async def _run_function_fixture(session_db: str) -> str:
    """Drive the per-test ``vibetuner_db`` body directly.

    Bypasses the pytest fixture decorator so the test exercises the exact
    setup/teardown path without needing a session-scoped fixture in scope.
    """
    from vibetuner.testing import vibetuner_db

    gen = vibetuner_db.__wrapped__(session_db)
    db_name = await gen.__anext__()
    with pytest.raises(StopAsyncIteration):
        await gen.__anext__()
    return db_name


@pytest.mark.unit
class TestVibetunerDbFixtureCleanup:
    """The per-test ``vibetuner_db`` fixture must:

    - Reuse the session DB name (no per-test DB creation).
    - Wire Beanie with ``skip_indexes=True`` (indexes live on the shared DB).
    - Truncate non-system collections before AND after the test.
    - Reset ``mongo_client`` on teardown so the next test's event loop gets
      a fresh ``AsyncMongoClient``.
    """

    async def test_function_fixture_truncates_and_resets_client(self):
        mock_collection = MagicMock()
        mock_collection.delete_many = AsyncMock()

        mock_database = MagicMock()
        mock_database.list_collection_names = AsyncMock(
            return_value=["users", "posts", "system.indexes"]
        )
        mock_database.__getitem__ = MagicMock(return_value=mock_collection)

        mock_client = MagicMock()
        mock_client.__getitem__ = MagicMock(return_value=mock_database)
        mock_client.close = AsyncMock()

        init_beanie_mock = AsyncMock()

        with (
            patch.object(mongo_mod, "mongo_client", None),
            patch(
                "vibetuner.mongo._ensure_client",
                side_effect=lambda: setattr(mongo_mod, "mongo_client", mock_client),
            ),
            patch("beanie.init_beanie", init_beanie_mock),
            patch("vibetuner.mongo.get_all_models", return_value=[]),
        ):
            db_name = await _run_function_fixture("test_session_abcd1234")

            assert db_name == "test_session_abcd1234"

            init_beanie_mock.assert_awaited_once()
            assert init_beanie_mock.await_args.kwargs["skip_indexes"] is True

            # Truncated twice (setup + teardown), skipping system.* collections.
            assert mock_database.list_collection_names.await_count == 2
            assert (
                mock_collection.delete_many.await_count == 4
            )  # 2 collections x 2 passes

            mock_client.close.assert_awaited_once()
            assert mongo_mod.mongo_client is None
