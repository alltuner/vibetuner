from datetime import datetime
from functools import cached_property
from typing import Annotated

import yaml
from pydantic import (
    UUID4,
    Field,
    MongoDsn,
    RedisDsn,
)
from pydantic_extra_types.language_code import LanguageAlpha2
from pydantic_settings import BaseSettings, SettingsConfigDict

from .core import paths


current_year: int = datetime.now().year


class ProjectConfiguration(BaseSettings):
    project_slug: str = "default_project"
    project_name: str = "default_project"

    project_description: str = "A default project description."

    # Language Related Settings
    supported_languages: set[LanguageAlpha2] | None = None
    default_language: LanguageAlpha2 = LanguageAlpha2("en")

    mongodb_url: MongoDsn | None = None
    redis_url: RedisDsn | None = None

    # AWS Parameters
    aws_default_region: str = "eu-central-1"

    # Company Name
    company_name: str = "All Tuner Labs"

    # From Email for transactional emails
    from_email: str = "corp@alltuner.com"

    # Copyright
    copyright_start: Annotated[int, Field(strict=True, gt=1714, lt=2048)] = current_year

    # Analytics
    umami_website_id: UUID4 | None = None

    # Fully Qualified Domain Name
    fqdn: str | None = None

    @cached_property
    def languages(self) -> set[str]:
        """Return the supported languages as a set of strings."""
        if self.supported_languages is None:
            return {self.language}

        return {
            str(lang) for lang in (*self.supported_languages, self.default_language)
        }

    @cached_property
    def language(self) -> str:
        """Return the default language as a string."""
        return str(self.default_language)

    @cached_property
    def copyright(self) -> str:
        year_part = (
            f"{self.copyright_start}-{current_year}"
            if self.copyright_start and self.copyright_start != current_year
            else str(current_year)
        )
        return f"© {year_part}{f' {self.company_name}' if self.company_name else ''}"

    model_config = SettingsConfigDict(extra="ignore")


project_settings: ProjectConfiguration = (
    ProjectConfiguration()
    if not paths.config_vars.exists()
    else ProjectConfiguration(
        **yaml.safe_load(paths.config_vars.read_text(encoding="utf-8"))
    )
)
