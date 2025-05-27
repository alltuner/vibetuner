import arel

from .. import paths


hotreload = arel.HotReload(
    paths=[arel.Path(str(paths.statics)), arel.Path(str(paths.templates))],
    reconnect_interval=2,
)
