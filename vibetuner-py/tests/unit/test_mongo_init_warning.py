# ABOUTME: Tests for init_mongodb diagnostic logging.
# ABOUTME: Covers missing MONGODB_URL warnings and connection failure error messages.
# ruff: noqa: S101

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pymongo.errors import ConnectionFailure


@pytest.mark.asyncio
async def test_warns_when_models_registered_but_no_mongodb_url():
    """init_mongodb should log a warning when user models exist but MONGODB_URL is unset."""
    mock_app_config = MagicMock()
    mock_app_config.models = [MagicMock()]  # One user model registered

    with (
        patch("vibetuner.mongo.settings", MagicMock(mongodb_url=None)),
        patch("vibetuner.mongo.load_app_config", return_value=mock_app_config),
        patch("vibetuner.mongo.logger") as mock_logger,
    ):
        from vibetuner.mongo import init_mongodb

        await init_mongodb()

        mock_logger.warning.assert_called_once()
        warning_msg = mock_logger.warning.call_args[0][0]
        assert "MONGODB_URL" in warning_msg


@pytest.mark.asyncio
async def test_silent_skip_when_no_models_and_no_mongodb_url():
    """init_mongodb should debug-log (not warn) when no user models are registered."""
    mock_app_config = MagicMock()
    mock_app_config.models = []  # No user models

    with (
        patch("vibetuner.mongo.settings", MagicMock(mongodb_url=None)),
        patch("vibetuner.mongo.load_app_config", return_value=mock_app_config),
        patch("vibetuner.mongo.logger") as mock_logger,
    ):
        from vibetuner.mongo import init_mongodb

        await init_mongodb()

        mock_logger.warning.assert_not_called()
        mock_logger.debug.assert_called()


@pytest.mark.asyncio
async def test_logs_error_on_connection_failure():
    """init_mongodb should log a clear error when MongoDB is unreachable."""
    mock_url = MagicMock()
    mock_url.host = "mongo.example.com"
    mock_url.port = 27017

    mock_settings = MagicMock(mongodb_url=mock_url, mongo_dbname="testdb")
    mock_client = MagicMock()
    mock_client.__getitem__ = MagicMock(return_value=MagicMock())

    with (
        patch("vibetuner.mongo.settings", mock_settings),
        patch("vibetuner.mongo.load_app_config", return_value=MagicMock(models=[])),
        patch("vibetuner.mongo.mongo_client", mock_client),
        patch("vibetuner.mongo._ensure_client"),
        patch(
            "vibetuner.mongo.init_beanie",
            new_callable=AsyncMock,
            side_effect=ConnectionFailure("connection refused"),
        ),
        patch("vibetuner.mongo.logger") as mock_logger,
    ):
        from vibetuner.mongo import init_mongodb

        with pytest.raises(ConnectionFailure):
            await init_mongodb()

        mock_logger.error.assert_called_once()
        error_msg = mock_logger.error.call_args[0][0]
        assert "Failed to connect to MongoDB" in error_msg
        fmt_args = mock_logger.error.call_args[0]
        assert "mongo.example.com:27017" in fmt_args[1]


class TestMongoEndpoint:
    """_mongo_endpoint must resolve a host:port from real DSN types."""

    def test_resolves_single_host_mongodsn(self):
        """MongoDsn exposes hosts via hosts(), not .host/.port."""
        from pydantic import MongoDsn
        from vibetuner.mongo import _mongo_endpoint

        assert (
            _mongo_endpoint(MongoDsn("mongodb://localhost:27018/")) == "localhost:27018"
        )

    def test_resolves_multi_host_mongodsn(self):
        """A replica-set DSN lists every host."""
        from pydantic import MongoDsn
        from vibetuner.mongo import _mongo_endpoint

        endpoint = _mongo_endpoint(MongoDsn("mongodb://a:27017,b:27018/"))
        assert endpoint == "a:27017,b:27018"

    def test_returns_unknown_for_none(self):
        from vibetuner.mongo import _mongo_endpoint

        assert _mongo_endpoint(None) == "unknown"
