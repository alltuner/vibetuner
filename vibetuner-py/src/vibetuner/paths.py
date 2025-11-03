from importlib.resources import files
from pathlib import Path

# Package-relative paths (for bundled templates in the vibetuner package)
_package_files = files("vibetuner")
_package_templates_traversable = _package_files / "templates"

# Convert to Path when actually used (handles both filesystem and zip-based packages)
def _get_package_templates_path() -> Path:
    """Get package templates path, works for both installed and editable installs."""
    # For most cases, we can convert directly to Path
    # For zip files, importlib.resources handles extraction automatically
    try:
        return Path(str(_package_templates_traversable))
    except (TypeError, ValueError):
        # If we can't convert to Path, we're in a zip or similar
        # In this case, we'll need to use as_file() context manager when accessing
        # For now, raise an error - we can enhance this later if needed
        raise RuntimeError(
            "Package templates are in a non-filesystem location. "
            "This is not yet supported."
        )


package_templates = _get_package_templates_path()

# Project root (set at runtime by the application using vibetuner)
# When None, only package templates are available
root: Path | None = None
fallback_path = "defaults"


def set_project_root(project_root: Path) -> None:
    """Set the project root directory for the application using vibetuner.

    This enables access to project-specific templates, assets, and locales.
    Must be called before accessing project-specific paths.
    """
    global root, templates, app_templates, locales, config_vars
    global assets, statics, css, js, favicons, img
    global frontend_templates, email_templates, markdown_templates

    root = project_root

    # Update project-specific paths
    templates = root / "templates"
    app_templates = templates  # Deprecated: projects now use templates/ directly
    locales = root / "locales"
    config_vars = root / ".copier-answers.yml"

    # Update asset paths
    assets = root / "assets"
    statics = assets / "statics"
    css = statics / "css"
    js = statics / "js"
    favicons = statics / "favicons"
    img = statics / "img"

    # Update template lists to include project overrides
    frontend_templates = [templates / "frontend", package_templates / "frontend"]
    email_templates = [templates / "email", package_templates / "email"]
    markdown_templates = [templates / "markdown", package_templates / "markdown"]


def to_template_path_list(path: Path) -> list[Path]:
    return [
        path,
        path / fallback_path,
    ]


def fallback_static_default(static_type: str, file_name: str) -> Path:
    """Return a fallback path for a file."""
    if root is None:
        raise RuntimeError(
            "Project root not set. Call set_project_root() before accessing assets."
        )

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


# Core templates point to package (always available)
core_templates = package_templates

# Template paths - initially only package templates, updated when set_project_root() is called
frontend_templates = [package_templates / "frontend"]
email_templates = [package_templates / "email"]
markdown_templates = [package_templates / "markdown"]

# Project-specific paths - will be None until set_project_root() is called
# These get updated by set_project_root()
templates: Path | None = None
app_templates: Path | None = None
locales: Path | None = None
config_vars: Path | None = None
assets: Path | None = None
statics: Path | None = None
css: Path | None = None
js: Path | None = None
favicons: Path | None = None
img: Path | None = None
