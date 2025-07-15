from . import paths, templates
from .config import project_settings, settings
from .context import Context
from .logging import logger


try:
    from ._version import version as __version__
except ImportError:
    __version__ = "0.0.0-default"

version = __version__

__all__ = [
    "Context",
    "logger",
    "paths",
    "project_settings",
    "settings",
    "templates",
    "version",
]
