import base64
import hashlib
from datetime import datetime
from functools import cached_property
from pathlib import Path
from typing import Annotated

import yaml
from pydantic import (
    UUID4,
    Field,
    SecretStr,
    computed_field,
)
from pydantic_extra_types.language_code import LanguageAlpha2
from pydantic_settings import BaseSettings, SettingsConfigDict

from . import paths
from ._version import version


current_year: int = datetime.now().year


class ProjectConfiguration(BaseSettings):
    project_name: str
    project_description: str

    # Language Related Settings
    supported_languages: set[LanguageAlpha2] | None = None
    default_language: LanguageAlpha2 = LanguageAlpha2("en")

    # Company Name
    company_name: str = "Acme Corp"

    # Copyright
    copyright_start: Annotated[int, Field(strict=True, gt=1714, lt=2048)] = current_year

    # Analytics
    umami_website_id: UUID4 | None = None

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


project_settings = ProjectConfiguration(
    **yaml.safe_load(
        Path(paths.root / ".copier-answers.yml").read_text(encoding="utf-8")
    )
)  # type: ignore[missing-argument]


class Configuration(BaseSettings):
    # Debug
    debug: bool = False

    # Version
    version: str = version

    # Session Key for FastAPI
    session_key: SecretStr = SecretStr("ct-!secret-must-change-me")

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def v_hash(self) -> str:
        hash_object = hashlib.sha256(self.version.encode("utf-8"))
        hash_bytes = hash_object.digest()

        # Convert to base64 and make URL-safe
        b64_hash = base64.urlsafe_b64encode(hash_bytes).decode("utf-8")

        # Remove padding characters and truncate to desired length
        url_safe_hash = b64_hash.rstrip("=")[:8]

        return url_safe_hash

    # Add here your configuration variables between this comment and the next one
    # No need to change anything Below
    model_config = SettingsConfigDict(case_sensitive=False, extra="ignore")


settings = Configuration()  # ty: ignore[missing-argument]
