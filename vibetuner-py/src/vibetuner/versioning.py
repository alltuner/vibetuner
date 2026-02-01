# ABOUTME: Version management with branch-based dev suffixes.
# ABOUTME: Reads version from APP_VERSION env var (Docker) or pyproject.toml (local dev).

import os

from git import InvalidGitRepositoryError, Repo

from vibetuner.pyproject import get_project_version


def _get_git_branch() -> str | None:
    """Get current git branch name, or None if not in a git repo."""
    try:
        repo = Repo(search_parent_directories=True)
        return repo.active_branch.name
    except (InvalidGitRepositoryError, TypeError):
        # TypeError is raised when HEAD is detached
        return None


def _branch_to_suffix(branch: str | None) -> str:
    """Convert branch name to semver-compatible suffix."""
    if not branch or branch in ("main", "master"):
        return "-dev"
    # Sanitize: feat/login-page → feat-login-page
    return "-" + branch.replace("/", "-").replace("_", "-")


def _is_production() -> bool:
    """Check if running in production environment."""
    return os.getenv("ENVIRONMENT", "dev").lower() == "prod"


def _get_base_version() -> str:
    """Get base version from APP_VERSION env var or pyproject.toml."""
    return os.getenv("APP_VERSION") or get_project_version()


def get_version() -> str:
    """Get version with optional dev suffix."""
    base = _get_base_version()
    if _is_production():
        return base
    suffix = _branch_to_suffix(_get_git_branch())
    return f"{base}{suffix}"


# Module-level exports
version = get_version()
__version__ = version
