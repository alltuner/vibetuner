import arel

from ..core import paths


hotreload = arel.HotReload(
    paths=[
        arel.Path(str(paths.js)),
        arel.Path(str(paths.css)),
        arel.Path(str(paths.templates)),
    ],
    reconnect_interval=2,
)
