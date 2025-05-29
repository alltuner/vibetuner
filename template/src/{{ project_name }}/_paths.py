from pathlib import Path


ROOT_PROJECT_DIR: Path = Path(__file__).resolve().parent.parent.parent

# Project paths
root = ROOT_PROJECT_DIR
assets = ROOT_PROJECT_DIR / "assets"
locales = ROOT_PROJECT_DIR / "locales"

# Frontend paths
frontend = ROOT_PROJECT_DIR / "frontend"
templates = frontend / "templates"
markdown = frontend / "markdown"

# Frontend static paths
statics = frontend / "statics"
css = statics / "css"
js = statics / "js"
favicons = statics / "favicons"
img = statics / "img"
