# ABOUTME: Tests for the vibetuner doctor CLI command.
# ABOUTME: Validates diagnostic checks for project structure, env vars, and services.
# ruff: noqa: S101
"""Tests for the vibetuner doctor command."""

from pathlib import Path
from unittest.mock import patch

from vibetuner.cli.doctor import (
    CheckResult,
    _check_dependencies,
    _check_env_vars,
    _check_port_availability,
    _check_project_structure,
    _check_templates,
    _check_tune_py,
)


class TestCheckProjectStructure:
    """Tests for project structure validation."""

    def test_no_project_root(self):
        results = _check_project_structure(None)
        assert len(results) == 1
        assert results[0].status == "error"
        assert "Not in a vibetuner project" in results[0].message

    def test_valid_project_structure(self, tmp_path):
        (tmp_path / ".copier-answers.yml").write_text("project_slug: test\n")
        (tmp_path / ".env").write_text("FOO=bar\n")
        src = tmp_path / "src" / "test_app"
        src.mkdir(parents=True)

        results = _check_project_structure(tmp_path)
        statuses = {r.name: r.status for r in results}

        assert statuses["Project root"] == "ok"
        assert statuses[".copier-answers.yml"] == "ok"
        assert statuses[".env file"] == "ok"
        assert statuses["src/ layout"] == "ok"

    def test_missing_copier_answers(self, tmp_path):
        (tmp_path / ".env").write_text("FOO=bar\n")
        (tmp_path / "src" / "app").mkdir(parents=True)

        results = _check_project_structure(tmp_path)
        statuses = {r.name: r.status for r in results}

        assert statuses[".copier-answers.yml"] == "error"

    def test_missing_env_file(self, tmp_path):
        (tmp_path / ".copier-answers.yml").write_text("project_slug: test\n")
        (tmp_path / "src" / "app").mkdir(parents=True)

        results = _check_project_structure(tmp_path)
        statuses = {r.name: r.status for r in results}

        assert statuses[".env file"] == "warn"

    def test_missing_src_dir(self, tmp_path):
        (tmp_path / ".copier-answers.yml").write_text("project_slug: test\n")

        results = _check_project_structure(tmp_path)
        statuses = {r.name: r.status for r in results}

        assert statuses["src/ layout"] == "error"


class TestCheckTunePy:
    """Tests for tune.py validation."""

    def test_no_project_root(self):
        results = _check_tune_py(None)
        assert results[0].status == "skip"

    @patch("vibetuner.pyproject.get_project_name", return_value=None)
    def test_no_package_name(self, _mock):
        results = _check_tune_py(Path("/fake"))
        assert results[0].status == "skip"

    @patch("vibetuner.pyproject.get_project_name", return_value="myapp")
    def test_tune_py_not_found(self, _mock, tmp_path):
        (tmp_path / "src" / "myapp").mkdir(parents=True)
        results = _check_tune_py(tmp_path)
        assert results[0].status == "warn"
        assert "zero-config" in results[0].message


class TestCheckEnvVars:
    """Tests for environment variable checks."""

    def test_default_session_key_warns(self):
        results = _check_env_vars()
        # Should contain at least Environment and SESSION_KEY checks
        names = {r.name for r in results}
        assert "Environment" in names
        assert "SESSION_KEY" in names

        session = next(r for r in results if r.name == "SESSION_KEY")
        assert session.status == "warn"


class TestCheckTemplates:
    """Tests for template validation."""

    def test_no_project_root(self):
        results = _check_templates(None)
        assert results[0].status == "skip"

    def test_no_templates_dir(self, tmp_path):
        results = _check_templates(tmp_path)
        assert results[0].status == "warn"

    def test_valid_templates(self, tmp_path):
        tpl_dir = tmp_path / "templates"
        tpl_dir.mkdir()
        (tpl_dir / "index.html").write_text("{% block content %}{% endblock %}")

        results = _check_templates(tmp_path)
        statuses = {r.name: r.status for r in results}

        assert statuses["Templates dir"] == "ok"
        assert statuses["Template syntax"] == "ok"

    def test_template_syntax_issue(self, tmp_path):
        tpl_dir = tmp_path / "templates"
        tpl_dir.mkdir()
        # Unmatched {%  — one open tag, no close tag
        (tpl_dir / "broken.html").write_text("{% block content")

        results = _check_templates(tmp_path)
        syntax_result = next(r for r in results if r.name == "Template syntax")
        assert syntax_result.status == "warn"


class TestCheckDependencies:
    """Tests for dependency checks."""

    def test_vibetuner_installed(self):
        results = _check_dependencies()
        vt = next(r for r in results if r.name == "vibetuner")
        assert vt.status == "ok"
        assert vt.message.startswith("v")

    def test_key_packages_checked(self):
        results = _check_dependencies()
        names = {r.name for r in results}
        assert "fastapi" in names
        assert "pydantic" in names


class TestCheckPortAvailability:
    """Tests for port availability checks."""

    def test_returns_results_for_both_ports(self):
        results = _check_port_availability()
        labels = {r.name for r in results}
        assert "Frontend (8000)" in labels
        assert "Worker UI (11111)" in labels


class TestCheckResult:
    """Tests for CheckResult data class."""

    def test_check_result_attributes(self):
        r = CheckResult("Test", "ok", "All good")
        assert r.name == "Test"
        assert r.status == "ok"
        assert r.message == "All good"
