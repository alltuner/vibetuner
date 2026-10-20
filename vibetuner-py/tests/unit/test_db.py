# ABOUTME: Tests for the database CLI commands.
# ABOUTME: Verifies dynamic model import uses project slug instead of hardcoded "app".
# ruff: noqa: S101
import sys
from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import Result
from typer.testing import CliRunner
from vibetuner.cli.db import db_app


runner = CliRunner()


@pytest.fixture()
def project_package(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Generator[Path, None, None]:
    """Put an importable ``myproject`` package on ``sys.path`` for one test.

    The command runs against real import machinery: a hand-built
    ``ModuleNotFoundError`` whose ``name`` names a submodule of a package that
    does not exist cannot arise from an actual import, and CPython 3.15 raises
    while rendering one.
    """
    package_dir = tmp_path / "myproject"
    package_dir.mkdir()
    (package_dir / "__init__.py").write_text("")
    monkeypatch.syspath_prepend(str(tmp_path))

    yield package_dir

    for name in [
        name
        for name in sys.modules
        if name == "myproject" or name.startswith("myproject.")
    ]:
        del sys.modules[name]


class TestCreateSchemaModelImport:
    """Tests that create-schema imports models using the project's package name."""

    def _invoke(self) -> Result:
        """Invoke create-schema via the CLI runner, returning the result."""
        return runner.invoke(db_app, [])

    def test_uses_project_name_for_model_import(self, project_package: Path) -> None:
        """Import path should use get_project_name() not hardcoded 'app'."""
        (project_package / "models.py").write_text("")

        with (
            patch("vibetuner.pyproject.get_project_name", return_value="myproject"),
            patch("vibetuner.cli.db.asyncer") as mock_asyncer,
        ):
            mock_asyncer.runnify.return_value = MagicMock()
            result = self._invoke()

        assert result.exit_code == 0
        assert "myproject.models" in sys.modules

    def test_skips_import_when_no_project_name(self, project_package: Path) -> None:
        """When not in a project directory, skip model import gracefully."""
        (project_package / "models.py").write_text("")

        with (
            patch("vibetuner.pyproject.get_project_name", return_value=None),
            patch("vibetuner.cli.db.asyncer") as mock_asyncer,
        ):
            mock_asyncer.runnify.return_value = MagicMock()
            result = self._invoke()

        assert result.exit_code == 0
        assert "myproject.models" not in sys.modules

    def test_warns_when_models_module_not_found(self, project_package: Path) -> None:
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
        assert "not found" in warning_args
        assert "myproject.models" in warning_args

    def test_warns_on_import_error(self, project_package: Path) -> None:
        """When models exist but have import errors, log a warning and continue."""
        (project_package / "models.py").write_text(
            'raise ImportError("broken dependency")\n'
        )

        with (
            patch("vibetuner.pyproject.get_project_name", return_value="myproject"),
            patch("vibetuner.logging.logger") as mock_logger,
            patch("vibetuner.cli.db.asyncer") as mock_asyncer,
        ):
            mock_asyncer.runnify.return_value = MagicMock()
            result = self._invoke()

        assert result.exit_code == 0
        mock_logger.warning.assert_called_once()
        assert "broken dependency" in str(mock_logger.warning.call_args)

    def test_warns_when_models_dependency_is_missing(
        self, project_package: Path
    ) -> None:
        """A dependency missing from models is reported as a failed import."""
        (project_package / "models.py").write_text("import absent_dependency\n")

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
        assert "Failed to import" in warning_args
        assert "myproject.models" in warning_args
        assert "absent_dependency" in warning_args
