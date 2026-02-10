# ABOUTME: Tests for pyproject.toml reading and project metadata.
# ABOUTME: Verifies get_project_name warns when pyproject.toml is missing but project exists.
# ruff: noqa: S101
from io import StringIO
from unittest.mock import patch

from loguru import logger
from vibetuner.pyproject import get_project_name, read_pyproject


class TestGetProjectName:
    """Tests for get_project_name function."""

    def setup_method(self):
        read_pyproject.cache_clear()

    def teardown_method(self):
        read_pyproject.cache_clear()

    def test_returns_none_when_no_root(self):
        """When paths.root is None, returns None without warning."""
        with patch("vibetuner.pyproject.paths", root=None):
            assert get_project_name() is None

    def test_returns_name_from_pyproject(self, tmp_path):
        """When pyproject.toml exists, returns the project name."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "myapp"\n')

        with patch("vibetuner.pyproject.paths", root=tmp_path):
            assert get_project_name() == "myapp"

    def test_warns_when_pyproject_missing_but_copier_answers_exists(self, tmp_path):
        """When pyproject.toml is missing but .copier-answers.yml exists, logs a warning."""
        copier_answers = tmp_path / ".copier-answers.yml"
        copier_answers.write_text("_src_path: gh:alltuner/vibetuner\n")

        sink = StringIO()
        handler_id = logger.add(sink, format="{message}", level="WARNING")
        try:
            with patch("vibetuner.pyproject.paths", root=tmp_path):
                result = get_project_name()

            assert result is None
            output = sink.getvalue()
            assert "pyproject.toml" in output
            assert ".copier-answers.yml" in output
        finally:
            logger.remove(handler_id)

    def test_no_warning_when_both_missing(self, tmp_path):
        """When both pyproject.toml and .copier-answers.yml are missing, no warning."""
        sink = StringIO()
        handler_id = logger.add(sink, format="{message}", level="WARNING")
        try:
            with patch("vibetuner.pyproject.paths", root=tmp_path):
                result = get_project_name()

            assert result is None
            assert "pyproject.toml not found" not in sink.getvalue()
        finally:
            logger.remove(handler_id)
