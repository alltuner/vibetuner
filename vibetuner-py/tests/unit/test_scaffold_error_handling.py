# ABOUTME: Tests for scaffold command error handling helpers
# ABOUTME: Verifies exception chain preservation and debug traceback printing
# ruff: noqa: S101

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer
from vibetuner.cli.scaffold import (
    _handle_scaffold_error,
    _is_debug_mode,
    adopt,
    new,
    update,
)


class TestIsDebugMode:
    """Test the _is_debug_mode helper."""

    def test_false_when_debug_not_set(self):
        with patch.dict(os.environ, {}, clear=True):
            assert _is_debug_mode() is False

    def test_true_when_debug_is_1(self):
        with patch.dict(os.environ, {"DEBUG": "1"}):
            assert _is_debug_mode() is True

    def test_true_when_debug_is_true(self):
        with patch.dict(os.environ, {"DEBUG": "true"}):
            assert _is_debug_mode() is True

    def test_true_when_debug_is_yes(self):
        with patch.dict(os.environ, {"DEBUG": "yes"}):
            assert _is_debug_mode() is True

    def test_true_when_debug_is_uppercase(self):
        with patch.dict(os.environ, {"DEBUG": "TRUE"}):
            assert _is_debug_mode() is True

    def test_false_when_debug_is_0(self):
        with patch.dict(os.environ, {"DEBUG": "0"}):
            assert _is_debug_mode() is False

    def test_false_when_debug_is_empty(self):
        with patch.dict(os.environ, {"DEBUG": ""}):
            assert _is_debug_mode() is False


class TestHandleScaffoldError:
    """Test the _handle_scaffold_error helper."""

    def test_prints_friendly_message(self):
        """The one-line error message is always printed."""
        mock_console = MagicMock()
        e = RuntimeError("copier exploded")

        try:
            raise e
        except RuntimeError:
            with patch("vibetuner.cli.scaffold._console", return_value=mock_console):
                with patch.dict(os.environ, {}, clear=True):
                    _handle_scaffold_error(e, "creating project")

        mock_console.print.assert_called_once_with(
            "[red]Error creating project: copier exploded[/red]"
        )

    def test_no_traceback_without_debug(self):
        """print_exception is NOT called when DEBUG is not set."""
        mock_console = MagicMock()
        e = RuntimeError("something failed")

        try:
            raise e
        except RuntimeError:
            with patch("vibetuner.cli.scaffold._console", return_value=mock_console):
                with patch.dict(os.environ, {}, clear=True):
                    _handle_scaffold_error(e, "updating project")

        mock_console.print_exception.assert_not_called()

    def test_prints_traceback_in_debug_mode(self):
        """print_exception IS called when DEBUG=1."""
        mock_console = MagicMock()
        e = RuntimeError("copier task failed")

        try:
            raise e
        except RuntimeError:
            with patch("vibetuner.cli.scaffold._console", return_value=mock_console):
                with patch.dict(os.environ, {"DEBUG": "1"}):
                    _handle_scaffold_error(e, "adopting scaffolding")

        mock_console.print_exception.assert_called_once()


class TestExceptionChainPreservation:
    """Verify that raise ... from e preserves the original cause."""

    def test_new_command_preserves_cause(self, tmp_path: Path):
        """scaffold new: the Exit's __cause__ is the original copier exception."""
        original = RuntimeError("network timeout")

        with patch("copier.run_copy", side_effect=original):
            with patch.dict(os.environ, {}, clear=True):
                with pytest.raises(typer.Exit) as exc_info:
                    new(destination=tmp_path / "proj")

        assert exc_info.value.__cause__ is original

    def test_update_command_preserves_cause(self, tmp_path: Path):
        """scaffold update: the Exit's __cause__ is the original copier exception."""
        # Create .copier-answers.yml so validation passes
        (tmp_path / ".copier-answers.yml").write_text("project_slug: test\n")
        original = RuntimeError("git ref not found")

        with patch("copier.run_update", side_effect=original):
            with patch.dict(os.environ, {}, clear=True):
                with pytest.raises(typer.Exit) as exc_info:
                    update(path=tmp_path)

        assert exc_info.value.__cause__ is original

    def test_adopt_command_preserves_cause(self, tmp_path: Path):
        """scaffold adopt: the Exit's __cause__ is the original copier exception."""
        # Set up a valid project directory so validation passes
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "test"\ndependencies = ["vibetuner"]\n'
        )
        original = RuntimeError("template parse error")

        with patch("copier.run_copy", side_effect=original):
            with patch.dict(os.environ, {}, clear=True):
                with pytest.raises(typer.Exit) as exc_info:
                    adopt(path=tmp_path)

        assert exc_info.value.__cause__ is original

    def test_new_exit_code_is_1_on_failure(self, tmp_path: Path):
        """scaffold new: exit code is 1 when copier fails."""
        with patch("copier.run_copy", side_effect=RuntimeError("oops")):
            with patch.dict(os.environ, {}, clear=True):
                with pytest.raises(typer.Exit) as exc_info:
                    new(destination=tmp_path / "proj")

        assert exc_info.value.exit_code == 1
