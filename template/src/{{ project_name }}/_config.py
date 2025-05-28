from pathlib import Path
from typing import Annotated

import yaml
from pydantic import Field
from pydantic_extra_types.language_code import LanguageAlpha2
from pydantic_settings import BaseSettings, SettingsConfigDict

from . import paths


try:
    from ._version import version  # type: ignore
except ImportError:
    version: str = "no_version"

__version__: str = version  # type: ignore

Year = Annotated[int, Field(strict=True, gt=1980, lt=2100)]


class ProjectConfiguration(BaseSettings):
    project_name: str

    # Language Related Settings
    supported_languages: set[LanguageAlpha2] | None = None
    default_language: LanguageAlpha2 = LanguageAlpha2("en")

    # Analytics
    umami_website_id: str = ""

    @property
    def languages(self) -> set[str]:
        """Return the supported languages as a set of strings."""
        if self.supported_languages is None:
            return {self.language}

        return {
            str(lang) for lang in (*self.supported_languages, self.default_language)
        }

    @property
    def language(self) -> str:
        """Return the default language as a string."""
        return str(self.default_language)

    # Add here your configuration variables between this comment and the next one

    # No need to change anything Below
    model_config = SettingsConfigDict(extra="ignore")


project_settings = ProjectConfiguration(
    **yaml.safe_load(
        Path(paths.root / ".copier-answers.yml").read_text(encoding="utf-8")
    )
)  # type: ignore[missing-argument]


class Configuration(BaseSettings):
    # Debug
    debug: bool = Field(default=False)

    # Copyright
    copyright_start: Year | None = None
    copyright_current: Year = 2025

    # Company Name
    company_name: str | None = "Acme Corp"

    # Session Key for FastAPI
    session_key: str = "ct-!secret"

    # Add here your configuration variables between this comment and the next one
    # No need to change anything Below
    model_config = SettingsConfigDict(
        env_file=paths.root / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Configuration()
