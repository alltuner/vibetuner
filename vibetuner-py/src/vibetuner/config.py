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

from vibetuner.logging import logger

from .paths import config_vars as config_vars_path
from .versioning import version


current_year: int = datetime.now().year


def _load_project_config() -> "ProjectConfiguration":
    if config_vars_path is None:
        raise RuntimeError(
            "Project root not detected. Cannot load project configuration. "
            "Ensure you're running from within a project directory with .copier-answers.yml"
        )
    if not config_vars_path.exists():
        return ProjectConfiguration()

    yaml_data = yaml.safe_load(config_vars_path.read_text(encoding="utf-8"))
    return ProjectConfiguration(**yaml_data)


class ProjectConfiguration(BaseSettings):
    @classmethod
    def from_project_config(cls) -> "ProjectConfiguration":
        return _load_project_config()

    project_slug: str = "default_project"
    project_name: str = "default_project"

    project_description: str = "A default project description."

    # Language Related Settings
    supported_languages: set[LanguageAlpha2] | None = None
    default_language: LanguageAlpha2 = LanguageAlpha2("en")

    # AWS Parameters
    aws_default_region: str = "eu-central-1"

    # Company Name
    company_name: str = "Acme Corp"

    # From Email for transactional emails
    from_email: str = "no-reply@example.com"

    # Copyright
    copyright_start: Annotated[int, Field(strict=True, gt=1714, lt=2048)] = current_year

    # Analytics
    umami_website_id: UUID4 | None = None

    # Fully Qualified Domain Name
    fqdn: str | None = None

    @cached_property
    def languages(self) -> set[str]:
        if self.supported_languages is None:
            return {self.language}

        return {
            str(lang) for lang in (*self.supported_languages, self.default_language)
        }

    @cached_property
    def language(self) -> str:
        return str(self.default_language)

    @cached_property
    def copyright(self) -> str:
        year_part = (
            f"{self.copyright_start}-{current_year}"
            if self.copyright_start and self.copyright_start != current_year
            else str(current_year)
        )
        return f"© {year_part}{f' {self.company_name}' if self.company_name else ''}"

    model_config = SettingsConfigDict(case_sensitive=False, extra="ignore")


class CoreConfiguration(BaseSettings):
    project: ProjectConfiguration = ProjectConfiguration.from_project_config()

    debug: bool = False
    version: str = version
    session_key: SecretStr = SecretStr("ct-!secret-must-change-me")

    # Database and Cache URLs
    mongodb_url: MongoDsn = MongoDsn("mongodb://localhost:27017")
    redis_url: RedisDsn = RedisDsn("redis://localhost:6379")

    aws_access_key_id: SecretStr | None = None
    aws_secret_access_key: SecretStr | None = None

    r2_default_bucket_name: str | None = None
    r2_bucket_endpoint_url: HttpUrl | None = None
    r2_access_key: SecretStr | None = None
    r2_secret_key: SecretStr | None = None
    r2_default_region: str = "auto"

    @computed_field
    @cached_property
    def v_hash(self) -> str:
        hash_object = hashlib.sha256(self.version.encode("utf-8"))
        hash_bytes = hash_object.digest()

        b64_hash = base64.urlsafe_b64encode(hash_bytes).decode("utf-8")

        url_safe_hash = b64_hash.rstrip("=")[:8]

        return url_safe_hash

    @cached_property
    def mongo_dbname(self) -> str:
        return self.project.project_slug

    model_config = SettingsConfigDict(
        case_sensitive=False, extra="ignore", env_file=".env"
    )


settings = CoreConfiguration()


logger.info("Configuration loaded for project: {}", settings.project.project_name)
logger.info("Configuration loaded for project: {}", settings.model_dump())
