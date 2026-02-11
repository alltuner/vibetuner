# ABOUTME: Centralized pyproject.toml reading for project metadata.
# ABOUTME: Provides cached access to project name and version.

import tomllib
from functools import lru_cache

from vibetuner.logging import logger
from vibetuner.paths import paths


@lru_cache
def read_pyproject() -> dict:
    """Read and cache pyproject.toml from project root."""
    if not paths.root:
        return {}
    pyproject_file = paths.root / "pyproject.toml"
    if not pyproject_file.exists():
        if (paths.root / ".copier-answers.yml").exists():
            logger.warning(
                "pyproject.toml not found in project root ({}), but "
                ".copier-answers.yml exists. This usually means pyproject.toml "
                "was not copied into the runtime environment. Custom tune.py "
                "configuration will be ignored.",
                paths.root,
            )
        return {}
    return tomllib.load(pyproject_file.open("rb"))


def get_project_name() -> str | None:
    """Get project name from pyproject.toml, normalized for use as a Python module name.

    Converts hyphens to underscores per PEP 503 / Python packaging convention
    (e.g., ``my-cool-app`` -> ``my_cool_app``).
    """
    name = read_pyproject().get("project", {}).get("name")
    if name is not None:
        return name.replace("-", "_")
    return None


def get_project_version() -> str:
    """Get project version from pyproject.toml."""
    return read_pyproject().get("project", {}).get("version", "0.0.0")
