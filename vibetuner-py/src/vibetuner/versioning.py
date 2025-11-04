__version__ = "0.0.0-default"

try:
    from app._version import version as __version__  # type: ignore
except ImportError:
    pass

version = __version__
