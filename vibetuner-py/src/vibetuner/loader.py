# ABOUTME: Loads user's app configuration from tune.py.
# ABOUTME: Returns VibetunerApp with defaults if no tune.py exists.
from functools import lru_cache
from importlib import import_module

from vibetuner.app_config import VibetunerApp
from vibetuner.logging import logger
from vibetuner.pyproject import get_project_name


class ConfigurationError(Exception):
    """Raised when tune.py exists but is misconfigured."""


@lru_cache
def load_app_config() -> VibetunerApp:
    """Load the user's app configuration from tune.py, or return defaults.

    Returns:
        VibetunerApp instance with user's configuration or empty defaults.

    Raises:
        ConfigurationError: If tune.py exists but doesn't export 'app' correctly.
        Any import error from inside tune.py (syntax errors, broken imports, etc.)
    """
    package_name = get_project_name()

    if package_name is None:
        # Not in a project directory (e.g., running `vibetuner scaffold`)
        logger.debug("No project found, using default VibetunerApp config")
        return VibetunerApp()

    try:
        module = import_module(f"{package_name}.tune")
    except ModuleNotFoundError as e:
        # Check if tune.py is missing (ok, use defaults)
        # vs a broken import inside tune.py (re-raise)
        if e.name == f"{package_name}.tune":
            # No config file - use defaults (zero-config mode)
            logger.debug(f"No {package_name}/tune.py found, using default config")
            return VibetunerApp()
        # Broken import inside tune.py - surface the error
        raise
    except ImportError as e:
        raise ConfigurationError(
            f"Failed to import '{package_name}/tune.py': {e}\n"
            f"Hint: This often happens due to circular imports in your app modules."
        ) from e

    app_config = getattr(module, "app", None)

    if app_config is None:
        # Check if module was partially loaded (circular import symptom)
        hint = ""
        if hasattr(module, "__file__") and not hasattr(module, "__all__"):
            hint = (
                "\nHint: If you're seeing this during startup, it may be caused by "
                "a circular import. Check that tune.py doesn't import modules that "
                "import back from tune.py."
            )
        raise ConfigurationError(
            f"'{package_name}/tune.py' must export an 'app' object. "
            f"Example: app = VibetunerApp(routes=[...]){hint}"
        )

    if not isinstance(app_config, VibetunerApp):
        raise ConfigurationError(
            f"'app' in '{package_name}/tune.py' must be a VibetunerApp instance, "
            f"got {type(app_config).__name__}"
        )

    logger.info(f"Loaded app config from {package_name}.tune")
    return app_config
