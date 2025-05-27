from typing import Annotated

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from . import paths
from ._project import PROJECT_NAME


try:
    from ._version import version  # type: ignore
except ImportError:
    version: str = "no_version"

__version__: str = version  # type: ignore
__project_name__ = PROJECT_NAME

Year = Annotated[int, Field(strict=True, gt=1980, lt=2100)]


class Configuration(BaseSettings):
    # Debug
    debug: bool = Field(default=False)

    # Copyright
    copyright_start: Year | None = None
    copyright_current: Year = 2025

    # Company Name
    company_name: str | None = "Acme Corp"

    # Analytics
    umami_website_id: str = ""

    # Add here your configuration variables between this comment and the next one
    # No need to change anything Below

    model_config = SettingsConfigDict(
        env_file=paths.root / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Configuration()
