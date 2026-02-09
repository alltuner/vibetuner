# ABOUTME: Tests for the database CLI commands.
# ABOUTME: Verifies dynamic model import uses project slug instead of hardcoded "app".
# ruff: noqa: S101
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from vibetuner.cli.db import db_app

runner = CliRunner()


class TestCreateSchemaModelImport:
    """Tests that create-schema imports models using the project's package name."""

    def _invoke(self) -> object:
        """Invoke create-schema via the CLI runner, returning the result."""
        return runner.invoke(db_app, [])

    def test_uses_project_name_for_model_import(self):
        """Import path should use get_project_name() not hardcoded 'app'."""
        with (
            patch("vibetuner.pyproject.get_project_name", return_value="myproject"),
            patch("vibetuner.cli.db.asyncer") as mock_asyncer,
        ):
            mock_asyncer.runnify.return_value = MagicMock()

            real_import_module = __import__("importlib").import_module
            imported_modules: list[str] = []

            def tracking_import_module(name: str):
                imported_modules.append(name)
                if name == "myproject.models":
                    raise ModuleNotFoundError(name=name)
                return real_import_module(name)

            with patch("importlib.import_module", side_effect=tracking_import_module):
                result = self._invoke()

        assert result.exit_code == 0
        assert "myproject.models" in imported_modules

    def test_skips_import_when_no_project_name(self):
        """When not in a project directory, skip model import gracefully."""
        with (
            patch("vibetuner.pyproject.get_project_name", return_value=None),
            patch("vibetuner.cli.db.asyncer") as mock_asyncer,
        ):
            mock_asyncer.runnify.return_value = MagicMock()

            imported_modules: list[str] = []
            real_import_module = __import__("importlib").import_module

            def tracking_import_module(name: str):
                imported_modules.append(name)
                return real_import_module(name)

            with patch("importlib.import_module", side_effect=tracking_import_module):
                result = self._invoke()

        assert result.exit_code == 0
        assert not any(name.endswith(".models") for name in imported_modules)

    def test_warns_when_models_module_not_found(self):
        """When project.models doesn't exist, log a warning and continue."""
        with (
            patch("vibetuner.pyproject.get_project_name", return_value="myproject"),
            patch("vibetuner.logging.logger") as mock_logger,
            patch("vibetuner.cli.db.asyncer") as mock_asyncer,
        ):
            mock_asyncer.runnify.return_value = MagicMock()
            result = self._invoke()

        assert result.exit_code == 0
        mock_logger.warning.assert_called_once()
        warning_args = str(mock_logger.warning.call_args)
        assert "myproject" in warning_args

    def test_warns_on_import_error(self):
        """When models exist but have import errors, log a warning and continue."""
        real_import_module = __import__("importlib").import_module

        def failing_import_module(name: str):
            if name == "myproject.models":
                raise ImportError("broken dependency")
            return real_import_module(name)

        with (
            patch("vibetuner.pyproject.get_project_name", return_value="myproject"),
            patch("importlib.import_module", side_effect=failing_import_module),
            patch("vibetuner.logging.logger") as mock_logger,
            patch("vibetuner.cli.db.asyncer") as mock_asyncer,
        ):
            mock_asyncer.runnify.return_value = MagicMock()
            result = self._invoke()

        assert result.exit_code == 0
        mock_logger.warning.assert_called_once()
        assert "broken dependency" in str(mock_logger.warning.call_args)
