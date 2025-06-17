from pathlib import Path


root: Path = Path(__file__).resolve().parent.parent.parent

# Locales
locales = root / "locales"

# Config Vars
config_vars = root / ".copier-answers.yml"

# Template paths
templates = root / "templates"
frontend_templates = templates / "frontend"
email_templates = templates / "email"
markdown_templates = templates / "markdown"

# Asset paths
assets = root / "assets"
statics = assets / "statics"
css = statics / "css"
js = statics / "js"
favicons = statics / "favicons"
img = statics / "img"
