import tomllib
from importlib import import_module

from vibetuner.logging import logger
from vibetuner.paths import paths


def _package_name() -> str | None:
    """Get the current package name, or None if not in a package."""

    if not paths.root:
        return None

    pyproject_file = paths.root / "pyproject.toml"

    if not pyproject_file.exists():
        return None

    project_name = (
        tomllib.loads(pyproject_file.read_text()).get("project", {}).get("name", None)
    )

    return project_name if project_name else None


def import_module_by_name(module_name: str) -> None:
    """Dynamically import a module by name."""
    packages_to_try: list[str | None] = []
    # First, we check the legacy src/app structure
    packages_to_try.append("app")
    # Then, we check for the package name if available
    if package_name := _package_name():
        packages_to_try.append(package_name)

    # Lastly, we try the bare module name
    packages_to_try.append(None)

    for package in packages_to_try:
        try:
            logger.debug(
                f"Trying to import module '{module_name}' "
                f"from package '{package or 'top-level'}'."
            )

            module_to_import = f"{package}.{module_name}" if package else module_name

            module = import_module(module_to_import)
            logger.info(
                f"Successfully imported module '{module_name}' "
                f"from package '{package or 'top-level'}'."
            )
            return module
        except (ModuleNotFoundError, ImportError) as e:
            logger.debug(
                f"Failed to import module '{module_name}' "
                f"from package '{package or 'top-level'}': {e}"
            )
            continue

    raise ModuleNotFoundError(f"Module '{module_name}' not found in any known package.")
