import arel

from vibetuner.paths import css as css_path, js as js_path, templates as templates_path


hotreload = arel.HotReload(
    paths=[
        arel.Path(str(js_path)),
        arel.Path(str(css_path)),
        arel.Path(str(templates_path)),
    ],
    reconnect_interval=2,
)
