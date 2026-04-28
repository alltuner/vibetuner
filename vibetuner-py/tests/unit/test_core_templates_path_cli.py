# ABOUTME: Tests for the `vibetuner core-templates-path` CLI command.
# ABOUTME: Verifies stdout payload, no log noise, and that the path resolves to a real dir.
# ruff: noqa: S101

from pathlib import Path

from typer.testing import CliRunner
from vibetuner.cli import app


runner = CliRunner()


class TestCoreTemplatesPathCli:
    def test_prints_existing_directory(self):
        result = runner.invoke(app, ["core-templates-path"])
        assert result.exit_code == 0
        path = Path(result.stdout.strip())
        assert path.is_dir()

    def test_path_contains_skeleton_template(self):
        """Sanity check: it points at the framework's frontend templates."""
        result = runner.invoke(app, ["core-templates-path"])
        assert result.exit_code == 0
        path = Path(result.stdout.strip())
        assert (path / "base" / "skeleton.html.jinja").is_file()

    def test_stdout_is_just_the_path_no_log_noise(self):
        """Output is suitable for shell command substitution.

        ``CliRunner`` by default merges stderr into ``output``; ``stdout``
        contains only what's written to ``sys.stdout``. Loguru routes log
        records to stderr, so a clean ``stdout`` is what setup-tw-sources
        depends on.
        """
        result = runner.invoke(app, ["core-templates-path"])
        assert result.exit_code == 0
        # Single trailing newline, no extra whitespace, single line.
        assert result.stdout.endswith("\n")
        assert len(result.stdout.strip().splitlines()) == 1

    def test_path_is_absolute(self):
        result = runner.invoke(app, ["core-templates-path"])
        assert result.exit_code == 0
        path = Path(result.stdout.strip())
        assert path.is_absolute()
