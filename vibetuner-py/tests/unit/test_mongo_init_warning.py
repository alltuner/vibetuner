# ABOUTME: Tests that init_mongodb warns when models are registered but MONGODB_URL is missing.
# ABOUTME: Ensures users get actionable diagnostics instead of cryptic Beanie errors.
# ruff: noqa: S101

from unittest.mock import MagicMock, patch

import pytest


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
