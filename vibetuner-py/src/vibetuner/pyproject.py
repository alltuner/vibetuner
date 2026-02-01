# ABOUTME: Centralized pyproject.toml reading for project metadata.
# ABOUTME: Provides cached access to project name and version.

import tomllib
from functools import lru_cache

from vibetuner.paths import paths


@lru_cache
def read_pyproject() -> dict:
    """Read and cache pyproject.toml from project root."""
    if not paths.root:
        return {}
    pyproject_file = paths.root / "pyproject.toml"
    if not pyproject_file.exists():
        return {}
    return tomllib.load(pyproject_file.open("rb"))


def get_project_name() -> str | None:
    """Get project name from pyproject.toml."""
    return read_pyproject().get("project", {}).get("name")


def get_project_version() -> str:
    """Get project version from pyproject.toml."""
    return read_pyproject().get("project", {}).get("version", "0.0.0")
