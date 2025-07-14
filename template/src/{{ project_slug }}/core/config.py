import base64
import hashlib
from datetime import datetime
from functools import cached_property
from typing import Annotated

import yaml
from pydantic import (
    UUID4,
    Field,
    HttpUrl,
    MongoDsn,
    RedisDsn,
    SecretStr,
    computed_field,
)
from pydantic_extra_types.language_code import LanguageAlpha2
from pydantic_settings import BaseSettings, SettingsConfigDict

from .._version import version
from . import paths


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


class Configuration(BaseSettings):
    # Debug
    debug: bool = False

    # Version
    version: str = version

    # Session Key for FastAPI
    session_key: SecretStr = SecretStr("ct-!secret-must-change-me")

    # Amazon Credentials
    aws_access_key_id: SecretStr | None = None
    aws_secret_access_key: SecretStr | None = None

    # R2 Related Settings
    r2_default_bucket_name: str | None = None
    r2_bucket_endpoint_url: HttpUrl | None = None
    r2_access_key: SecretStr | None = None
    r2_secret_key: SecretStr | None = None
    r2_default_region: str = "auto"

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

    @cached_property
    def mongo_dbname(self) -> str:
        """Extract the database name from the MongoDB URL."""
        return project_settings.project_slug

    # Add here your configuration variables between this comment and the next one
    # No need to change anything Below
    model_config = SettingsConfigDict(case_sensitive=False, extra="ignore")


settings = Configuration()  # ty: ignore[missing-argument]
