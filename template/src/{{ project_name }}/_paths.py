from pathlib import Path


ROOT_PROJECT_DIR: Path = Path(__file__).resolve().parent.parent.parent

frontend = ROOT_PROJECT_DIR / "frontend"
statics = frontend / "statics"
templates = frontend / "templates"
