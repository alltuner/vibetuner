from importlib.resources import files
from pathlib import Path
from typing import Self

from pydantic import computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from vibetuner.logging import logger


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


def create_core_templates_symlink(target: Path) -> None:
    """Create or update a 'core' symlink pointing to the package templates directory."""

    try:
        source = _get_package_templates_path().resolve()
    except RuntimeError as e:
        logger.error(f"Cannot create symlink: {e}")
        return

    # Case 1: target is already a symlink → check if it needs updating
    if target.is_symlink():
        if target.resolve() != source:
            target.unlink()
            target.symlink_to(source, target_is_directory=True)
            logger.info(f"Updated symlink '{target}' → '{source}'")
        else:
            logger.debug(f"Symlink '{target}' already points to '{source}'")
        return

    # Case 2: target does not exist → create symlink
    if not target.exists():
        target.symlink_to(source, target_is_directory=True)
        logger.info(f"Created symlink '{target}' → '{source}'")
        return

    # Case 3: exists but is not a symlink → error
    logger.error(f"Cannot create symlink: '{target}' exists and is not a symlink.")
    raise FileExistsError(
        f"Cannot create symlink: '{target}' exists and is not a symlink."
    )


# Package templates always available
package_templates = _get_package_templates_path()


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

    @computed_field
    @property
    def fonts(self) -> Path | None:
        """Project fonts directory."""
        return self.root / "assets" / "statics" / "fonts" if self.root else None

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

    @computed_field
    @property
    def app_code(self) -> list[Path]:
        """Project application code directory."""
        code_paths: list[Path] = []

        if not self.root:
            return code_paths

        src_tree = self.root / "src"
        if src_tree.is_dir():
            code_paths.append(src_tree)

        app_path = self.root / "app.py"
        if app_path.is_file():
            code_paths.append(app_path)

        return code_paths

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

    @property
    def reload_paths(self) -> list[Path]:
        """Get list of paths to watch for reloads in dev mode."""

        paths = [
            p
            for group in (
                self.frontend_templates,
                self.email_templates,
                self.markdown_templates,
            )
            if group
            for p in group
            if p.is_dir()
        ] + self.app_code

        return paths


# Global settings instance with lazy auto-detection
paths = PathSettings()


def to_template_path_list(path: Path) -> list[Path]:
    """Convert path to list with fallback."""
    return paths.to_template_path_list(path)


def fallback_static_default(static_type: str, file_name: str) -> Path:
    """Return a fallback path for a static file."""
    return paths.fallback_static_default(static_type, file_name)


# Module-level variables that delegate to settings (backwards compatibility)
# Access like: from vibetuner.paths import frontend_templates
# Or better: from vibetuner.paths import paths; paths.frontend_templates
root = paths.root
templates = paths.templates
app_templates = paths.app_templates
locales = paths.locales
config_vars = paths.config_vars
assets = paths.assets
statics = paths.statics
css = paths.css
js = paths.js
favicons = paths.favicons
img = paths.img
fonts = paths.fonts
frontend_templates = paths.frontend_templates
email_templates = paths.email_templates
markdown_templates = paths.markdown_templates
