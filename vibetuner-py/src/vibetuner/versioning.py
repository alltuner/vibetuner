from vibetuner.logging import logger


__version__ = "0.0.0-default"

try:
    from app._version import version as __version__  # type: ignore
except (ImportError, ModuleNotFoundError) as e:
    # Log warning for both ImportError and ModuleNotFoundError as requested
    logger.warning(f"Failed to import app._version: {e}. Using default version.")

version = __version__
