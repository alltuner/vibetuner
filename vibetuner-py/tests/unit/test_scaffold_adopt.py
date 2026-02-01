# ABOUTME: Unit tests for vibetuner scaffold adopt command
# ABOUTME: Tests project data inference and validation logic
# ruff: noqa: S101

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner
from vibetuner.cli import app
from vibetuner.cli.scaffold import _infer_project_data


class TestInferProjectData:
    """Test the _infer_project_data helper function."""

    def test_infers_project_name_from_pyproject(self):
        """Test that project_name is inferred from pyproject.toml."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            pyproject = path / "pyproject.toml"
            pyproject.write_text(
                '[project]\nname = "my-awesome-project"\ndescription = "A test"\n'
            )

            data = _infer_project_data(path)
            assert data["project_name"] == "my-awesome-project"

    def test_infers_project_slug_from_name(self):
        """Test that project_slug is derived from project_name."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            pyproject = path / "pyproject.toml"
            pyproject.write_text(
                '[project]\nname = "My Awesome Project"\ndescription = "A test"\n'
            )

            data = _infer_project_data(path)
            assert data["project_slug"] == "my-awesome-project"

    def test_infers_description_from_pyproject(self):
        """Test that project_description is inferred from pyproject.toml."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            pyproject = path / "pyproject.toml"
            pyproject.write_text(
                '[project]\nname = "test"\ndescription = "A useful project"\n'
            )

            data = _infer_project_data(path)
            assert data["project_description"] == "A useful project"

    def test_infers_author_name_from_pyproject(self):
        """Test that author_name is inferred from pyproject.toml authors."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            pyproject = path / "pyproject.toml"
            pyproject.write_text(
                '[project]\nname = "test"\n'
                '[[project.authors]]\nname = "Jane Doe"\nemail = "jane@example.com"\n'
            )

            data = _infer_project_data(path)
            assert data["author_name"] == "Jane Doe"

    def test_infers_author_email_from_pyproject(self):
        """Test that author_email is inferred from pyproject.toml authors."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            pyproject = path / "pyproject.toml"
            pyproject.write_text(
                '[project]\nname = "test"\n'
                '[[project.authors]]\nname = "Jane Doe"\nemail = "jane@example.com"\n'
            )

            data = _infer_project_data(path)
            assert data["author_email"] == "jane@example.com"

    def test_falls_back_to_git_for_author_name(self):
        """Test that author_name falls back to git config when not in pyproject."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            pyproject = path / "pyproject.toml"
            pyproject.write_text('[project]\nname = "test"\n')

            mock_reader = MagicMock()
            mock_reader.get_value.return_value = "Git User"
            mock_repo = MagicMock()
            mock_repo.config_reader.return_value = mock_reader

            with patch("git.Repo", return_value=mock_repo):
                data = _infer_project_data(path)
                assert data["author_name"] == "Git User"
                mock_reader.get_value.assert_any_call("user", "name")

    def test_falls_back_to_git_for_author_email(self):
        """Test that author_email falls back to git config when not in pyproject."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            pyproject = path / "pyproject.toml"
            pyproject.write_text('[project]\nname = "test"\n')

            def mock_get_value(section, option):
                if section == "user" and option == "name":
                    return "Git User"
                if section == "user" and option == "email":
                    return "git@example.com"
                raise KeyError()

            mock_reader = MagicMock()
            mock_reader.get_value.side_effect = mock_get_value
            mock_repo = MagicMock()
            mock_repo.config_reader.return_value = mock_reader

            with patch("git.Repo", return_value=mock_repo):
                data = _infer_project_data(path)
                assert data["author_email"] == "git@example.com"

    def test_infers_python_version_from_file(self):
        """Test that python_version is inferred from .python-version file."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            pyproject = path / "pyproject.toml"
            pyproject.write_text('[project]\nname = "test"\n')
            python_version_file = path / ".python-version"
            python_version_file.write_text("3.13.1\n")

            data = _infer_project_data(path)
            assert data["python_version"] == "3.13"

    def test_extracts_major_minor_from_python_version(self):
        """Test that only major.minor is extracted from .python-version."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            pyproject = path / "pyproject.toml"
            pyproject.write_text('[project]\nname = "test"\n')
            python_version_file = path / ".python-version"
            python_version_file.write_text("3.12.8\n")

            data = _infer_project_data(path)
            assert data["python_version"] == "3.12"

    def test_handles_missing_python_version_file(self):
        """Test that missing .python-version file doesn't cause error."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            pyproject = path / "pyproject.toml"
            pyproject.write_text('[project]\nname = "test"\n')

            data = _infer_project_data(path)
            # Should not have python_version key if file doesn't exist
            assert "python_version" not in data

    def test_handles_missing_optional_fields(self):
        """Test that missing optional fields don't cause errors."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            pyproject = path / "pyproject.toml"
            pyproject.write_text('[project]\nname = "test"\n')

            # Mock git to return empty strings (simulating no git config)
            mock_result = MagicMock()
            mock_result.stdout = ""
            mock_result.returncode = 1

            with patch("subprocess.run", return_value=mock_result):
                data = _infer_project_data(path)
                assert data["project_name"] == "test"
                # Optional fields should not be present if not found
                assert "project_description" not in data
                assert "author_name" not in data
                assert "author_email" not in data


class TestAdoptValidation:
    """Test the adopt command validation logic."""

    def test_raises_for_nonexistent_path(self):
        """Test that adopt raises error for non-existent path."""
        runner = CliRunner()
        result = runner.invoke(app, ["scaffold", "adopt", "/nonexistent/path"])
        assert result.exit_code != 0
        assert "does not exist" in result.output

    def test_raises_for_missing_pyproject(self):
        """Test that adopt raises error when pyproject.toml is missing."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmp:
            result = runner.invoke(app, ["scaffold", "adopt", tmp])
            assert result.exit_code != 0
            assert "pyproject.toml" in result.output

    def test_raises_for_missing_vibetuner_dependency(self):
        """Test that adopt raises error when vibetuner is not a dependency."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            pyproject = path / "pyproject.toml"
            pyproject.write_text(
                '[project]\nname = "test"\ndependencies = ["fastapi"]\n'
            )

            result = runner.invoke(app, ["scaffold", "adopt", tmp])
            assert result.exit_code != 0
            assert "vibetuner" in result.output.lower()

    def test_raises_for_already_scaffolded_project(self):
        """Test that adopt raises error when .copier-answers.yml exists."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            pyproject = path / "pyproject.toml"
            pyproject.write_text(
                '[project]\nname = "test"\ndependencies = ["vibetuner"]\n'
            )
            answers = path / ".copier-answers.yml"
            answers.write_text("project_name: test\n")

            result = runner.invoke(app, ["scaffold", "adopt", tmp])
            assert result.exit_code != 0
            assert (
                "already" in result.output.lower() or "copier" in result.output.lower()
            )
