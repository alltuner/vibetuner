from pathlib import Path


root: Path = Path(__file__).resolve().parent.parent.parent
fallback_path = "default"


def to_template_path_list(path: Path) -> list[Path]:
    template_paths = [path]
    template_paths.append(path / fallback_path)

    return template_paths


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
