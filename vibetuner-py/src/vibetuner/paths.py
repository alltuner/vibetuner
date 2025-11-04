from importlib.resources import files
from pathlib import Path
from typing import Self

from pydantic import computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# Package-relative paths (for bundled templates in the vibetuner package)
_package_files = files("vibetuner")
_package_templates_traversable = _package_files / "templates"


def _get_package_templates_path() -> Path:
    """Get package templates path, works for both installed and editable installs."""
    try:
        return Path(str(_package_templates_traversable))
    except (TypeError, ValueError):
        raise RuntimeError(
            "Package templates are in a non-filesystem location. "
            "This is not yet supported."
        ) from None


# Package templates always available
package_templates = _get_package_templates_path()
core_templates = package_templates  # Alias for backwards compatibility


class PathSettings(BaseSettings):
    """Path settings with lazy auto-detection of project root."""

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
        validate_default=True,
    )

    root: Path | None = None
    fallback_path: str = "defaults"

    @model_validator(mode="after")
    def detect_project_root(self) -> Self:
        """Auto-detect project root if not explicitly set."""
        if self.root is None:
            detected = self._find_project_root()
            if detected is not None:
                self.root = detected
        return self

    @staticmethod
    def _find_project_root() -> Path | None:
        """Find project root by searching for marker files."""
        markers = [".copier-answers.yml", "pyproject.toml", ".git"]
        current = Path.cwd()

        for parent in [current, *current.parents]:
            if any((parent / marker).exists() for marker in markers):
                return parent

        return None

    # Project-specific paths (only available if root is set)
    @computed_field
    @property
    def templates(self) -> Path | None:
        """Project templates directory."""
        return self.root / "templates" if self.root else None

    @computed_field
    @property
    def app_templates(self) -> Path | None:
        """Deprecated: use templates instead."""
        return self.templates

    @computed_field
    @property
    def locales(self) -> Path | None:
        """Project locales directory."""
        return self.root / "locales" if self.root else None

    @computed_field
    @property
    def config_vars(self) -> Path | None:
        """Copier answers file."""
        return self.root / ".copier-answers.yml" if self.root else None

    @computed_field
    @property
    def assets(self) -> Path | None:
        """Project assets directory."""
        return self.root / "assets" if self.root else None

    @computed_field
    @property
    def statics(self) -> Path | None:
        """Project static assets directory."""
        return self.root / "assets" / "statics" if self.root else None

    @computed_field
    @property
    def css(self) -> Path | None:
        """Project CSS directory."""
        return self.root / "assets" / "statics" / "css" if self.root else None

    @computed_field
    @property
    def js(self) -> Path | None:
        """Project JavaScript directory."""
        return self.root / "assets" / "statics" / "js" if self.root else None

    @computed_field
    @property
    def favicons(self) -> Path | None:
        """Project favicons directory."""
        return self.root / "assets" / "statics" / "favicons" if self.root else None

    @computed_field
    @property
    def img(self) -> Path | None:
        """Project images directory."""
        return self.root / "assets" / "statics" / "img" if self.root else None

    # Template paths (always return a list, project + package)
    @computed_field
    @property
    def frontend_templates(self) -> list[Path]:
        """Frontend template search paths (project overrides, then package)."""
        paths = []
        if self.root:
            project_path = self.root / "templates" / "frontend"
            if project_path.exists():
                paths.append(project_path)
        paths.append(package_templates / "frontend")
        return paths

    @computed_field
    @property
    def email_templates(self) -> list[Path]:
        """Email template search paths (project overrides, then package)."""
        paths = []
        if self.root:
            project_path = self.root / "templates" / "email"
            if project_path.exists():
                paths.append(project_path)
        paths.append(package_templates / "email")
        return paths

    @computed_field
    @property
    def markdown_templates(self) -> list[Path]:
        """Markdown template search paths (project overrides, then package)."""
        paths = []
        if self.root:
            project_path = self.root / "templates" / "markdown"
            if project_path.exists():
                paths.append(project_path)
        paths.append(package_templates / "markdown")
        return paths

    def set_root(self, project_root: Path) -> None:
        """Explicitly set project root (overrides auto-detection)."""
        self.root = project_root

    def to_template_path_list(self, path: Path) -> list[Path]:
        """Convert path to list with fallback."""
        return [path, path / self.fallback_path]

    def fallback_static_default(self, static_type: str, file_name: str) -> Path:
        """Return a fallback path for a static file."""
        if self.statics is None:
            raise RuntimeError(
                "Project root not detected. Cannot access static assets."
            )

        paths_to_check = [
            self.statics / static_type / file_name,
            self.statics / self.fallback_path / static_type / file_name,
        ]

        for path in paths_to_check:
            if path.exists():
                return path

        raise FileNotFoundError(
            f"Could not find {file_name} in any of the fallback paths: {paths_to_check}"
        )


# Global settings instance with lazy auto-detection
_settings = PathSettings()


# Backwards-compatible module-level API
def set_project_root(project_root: Path) -> None:
    """Set the project root directory explicitly."""
    _settings.set_root(project_root)


def to_template_path_list(path: Path) -> list[Path]:
    """Convert path to list with fallback."""
    return _settings.to_template_path_list(path)


def fallback_static_default(static_type: str, file_name: str) -> Path:
    """Return a fallback path for a static file."""
    return _settings.fallback_static_default(static_type, file_name)


# Expose settings instance for direct access
paths = _settings

# Module-level variables that delegate to settings (backwards compatibility)
# Access like: from vibetuner.paths import frontend_templates
# Or better: from vibetuner.paths import paths; paths.frontend_templates
root = _settings.root
templates = _settings.templates
app_templates = _settings.app_templates
locales = _settings.locales
config_vars = _settings.config_vars
assets = _settings.assets
statics = _settings.statics
css = _settings.css
js = _settings.js
favicons = _settings.favicons
img = _settings.img
frontend_templates = _settings.frontend_templates
email_templates = _settings.email_templates
markdown_templates = _settings.markdown_templates
