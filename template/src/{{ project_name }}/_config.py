from pathlib import Path
from typing import Annotated

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from ._project import ENV_PREFIX, PROJECT_NAME


ROOT_PROJECT_DIR: Path = Path(__file__).resolve().parent.parent.parent

FRONTEND_DIR = ROOT_PROJECT_DIR / "frontend"
STATICS_DIR = FRONTEND_DIR / "statics"
TEMPLATES_DIR = FRONTEND_DIR / "templates"

try:
    from ._version import version  # type: ignore
except ImportError:
    version: str = "no_version"

__version__: str = version
__project_name__ = PROJECT_NAME

Year = Annotated[int, Field(strict=True, gt=1980, lt=2100)]


def get_copyright():
    if (
        settings.copyright_start is not None
        and settings.copyright_start != settings.copyright_current
    ):
        year_string = f"{settings.copyright_start}-{settings.copyright_current}"
    else:
        year_string = str(settings.copyright_current)

    if settings.company_name is not None:
        return f"© {year_string} {settings.company_name}"
    else:
        return f"© {year_string}"


class Configuration(BaseSettings):
    # Copyright
    copyright_start: Year | None = None
    copyright_current: Year = 2025

    # Company Name
    company_name: str | None = "All Tuner Labs"

    # Add here your configuration variables between this comment and the next one
    # No need to change anything Below

    model_config = SettingsConfigDict(
        env_file=ROOT_PROJECT_DIR / ".env",
        env_file_encoding="utf-8",
        env_prefix=ENV_PREFIX,
        case_sensitive=False,
        extra="ignore",
    )


settings = Configuration()
__copyright__ = get_copyright()
