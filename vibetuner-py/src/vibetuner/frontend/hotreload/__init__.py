# ABOUTME: Dev-only browser hot reload, watching this project's js, css and templates.
# ABOUTME: Vendored from arel 0.4.0+ (MIT, see LICENSE here); upstream's fix is unreleased.
from vibetuner.paths import paths

from .reloader import HotReload, Path


__all__ = ["HotReload", "Path", "hotreload"]

hotreload = HotReload(
    paths=[
        Path(str(paths.js)),
        Path(str(paths.css)),
        Path(str(paths.templates)),
    ],
    reconnect_interval=2,
)
