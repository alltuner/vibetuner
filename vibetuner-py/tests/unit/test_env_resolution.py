# ABOUTME: Tests that .env files are resolved relative to the project root.
# ABOUTME: Ensures CLI commands work correctly when run from subdirectories.
# ruff: noqa: S101

from unittest.mock import patch


class TestResolveEnvFiles:
    """Test .env file resolution relative to project root."""

    def test_resolves_env_files_from_project_root(self, tmp_path, monkeypatch):
        """When CWD is a subdirectory, .env paths should be anchored to project root."""
        # Create project root with marker file
        (tmp_path / ".copier-answers.yml").write_text("project_slug: test\n")
        (tmp_path / ".env").touch()

        # Create a subdirectory and set it as CWD
        subdir = tmp_path / "src" / "myapp"
        subdir.mkdir(parents=True)
        monkeypatch.chdir(subdir)

        from vibetuner.config import _resolve_env_files

        result = _resolve_env_files()

        assert str(tmp_path / ".env") in result
        assert str(tmp_path / ".env.local") in result

    def test_falls_back_to_relative_when_no_project_root(self, tmp_path, monkeypatch):
        """When no project root marker is found, fall back to relative paths."""
        # tmp_path has no marker files
        monkeypatch.chdir(tmp_path)

        from vibetuner.config import _resolve_env_files

        result = _resolve_env_files()

        assert result == (".env", ".env.local")

    def test_config_reads_env_from_project_root_subdirectory(
        self, tmp_path, monkeypatch
    ):
        """CoreConfiguration should pick up MONGODB_URL from .env at project root
        even when CWD is a subdirectory."""
        # Create project root with marker and .env
        (tmp_path / ".copier-answers.yml").write_text(
            "project_slug: test\nproject_name: Test\n"
        )
        (tmp_path / ".env").write_text("MONGODB_URL=mongodb://localhost:27017\n")

        # CWD is a subdirectory
        subdir = tmp_path / "src" / "myapp"
        subdir.mkdir(parents=True)
        monkeypatch.chdir(subdir)

        from vibetuner.config import (
            CoreConfiguration,
            ProjectConfiguration,
            _resolve_env_files,
        )

        env_files = _resolve_env_files()
        with patch.dict("os.environ", {}, clear=True):
            config = CoreConfiguration(
                project=ProjectConfiguration(project_slug="test", project_name="Test"),
                _env_file=env_files,
            )
            assert config.mongodb_url is not None
