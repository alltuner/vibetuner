# ABOUTME: Ensures the scaffolded pre-commit config lints with the project's own ruff,
# ABOUTME: so the hook can never drift from the ruff that vibetuner[dev] resolves.
# ruff: noqa: S101

from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
PRECOMMIT_CONFIG = REPO_ROOT / "vibetuner-template" / ".pre-commit-config.yaml"


def _repos() -> list[dict[str, Any]]:
    return yaml.safe_load(PRECOMMIT_CONFIG.read_text())["repos"]


def test_ruff_is_not_pinned_through_ruff_pre_commit() -> None:
    urls = [repo["repo"] for repo in _repos()]
    assert "https://github.com/astral-sh/ruff-pre-commit" not in urls


def test_ruff_check_hook_runs_the_locked_ruff() -> None:
    hooks = [
        hook
        for repo in _repos()
        if repo["repo"] == "local"
        for hook in repo["hooks"]
        if hook["id"] == "ruff-check"
    ]
    assert len(hooks) == 1
    assert hooks[0]["entry"].startswith("uv run --frozen ruff check")
    assert hooks[0]["language"] == "system"


def test_djlint_is_not_pinned_through_djlint_repo() -> None:
    urls = [repo["repo"] for repo in _repos()]
    assert "https://github.com/djlint/djLint" not in urls


def test_djlint_hook_runs_the_locked_djlint() -> None:
    hooks = [
        hook
        for repo in _repos()
        if repo["repo"] == "local"
        for hook in repo["hooks"]
        if hook["id"] == "djlint"
    ]
    assert len(hooks) == 1
    assert hooks[0]["entry"].startswith("uv run --frozen djlint")
    assert hooks[0]["language"] == "system"
