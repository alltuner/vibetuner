from pathlib import Path


root: Path = Path(__file__).resolve().parent.parent.parent.parent
fallback_path = "defaults"


def to_template_path_list(path: Path) -> list[Path]:
    return [
        path,
        path / fallback_path,
    ]


def fallback_static_default(static_type: str, file_name: str) -> Path:
    """Return a fallback path for a file."""

    paths_to_check = [
        statics / static_type / file_name,
        statics / fallback_path / static_type / file_name,
    ]

    for path in paths_to_check:
        if path.exists():
            return path

    raise FileNotFoundError(
        f"Could not find {file_name} in any of the fallback paths: {paths_to_check}"
    )


# Locales
locales = root / "locales"

# Config Vars
config_vars = root / ".copier-answers.yml"

# Template paths
templates = root / "templates"
frontend_templates = to_template_path_list(templates / "frontend")
email_templates = templates / "email"
markdown_templates = templates / "markdown"

# Asset paths
assets = root / "assets"
statics = assets / "statics"
css = statics / "css"
js = statics / "js"
favicons = statics / "favicons"
img = statics / "img"
