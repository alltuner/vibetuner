# ABOUTME: Detection utilities for optional vibetuner extras.
# ABOUTME: Provides availability checks and error messages for optional dependencies.
import types
from importlib import import_module
from importlib.util import find_spec


# Maps extra names to the packages they provide. Each entry is a tuple of
# (import_name, pip_extra_name) where import_name is what we try to import
# and pip_extra_name is what users install with `uv add 'vibetuner[extra]'`.
_EXTRA_MARKERS: dict[str, tuple[str, ...]] = {
    "mongo": ("beanie",),
    "auth": ("authlib",),
    "s3": ("aioboto3",),
    "blobs": ("aioboto3", "beanie"),
    "redis": ("redis",),
    "worker": ("streaq",),
    "rate-limit-redis": ("redis",),
    "i18n": ("starlette_babel",),
    "email": ("mailjet_rest", "resend"),
    "sql": ("sqlmodel",),
    "scaffold": ("copier",),
}

# Cache for extra availability checks
_cache: dict[str, bool] = {}


def has_extra(name: str) -> bool:
    """Check whether an optional extra is installed.

    Returns True if ALL marker packages for the given extra are importable.
    """
    if name not in _EXTRA_MARKERS:
        msg = f"Unknown extra: {name!r}"
        raise ValueError(msg)

    if name in _cache:
        return _cache[name]

    available = all(find_spec(pkg) is not None for pkg in _EXTRA_MARKERS[name])
    _cache[name] = available
    return available


def require_extra(name: str, feature: str | None = None) -> None:
    """Raise ImportError with guidance if an extra is not installed.

    Args:
        name: The extra name (e.g. "mongo", "auth").
        feature: Human-readable feature description for the error message.
                 If None, uses the extra name.
    """
    if has_extra(name):
        return

    feature_desc = feature or name
    msg = (
        f"{feature_desc} requires the '{name}' extra. "
        f"Install with: uv add 'vibetuner[{name}]'"
    )
    raise ImportError(msg)


def get_extras_status() -> dict[str, bool]:
    """Return the installation status of all known extras.

    Returns a sorted dict mapping extra names to their availability.
    """
    return {name: has_extra(name) for name in sorted(_EXTRA_MARKERS)}


def import_optional(
    module_name: str, extra: str, feature: str | None = None
) -> types.ModuleType:
    """Import a module that belongs to an optional extra.

    Returns the imported module if available, raises ImportError with
    guidance if not.
    """
    require_extra(extra, feature)
    return import_module(module_name)
