import base64
import hashlib
from datetime import datetime
from functools import cached_property

from pydantic import (
    HttpUrl,
    SecretStr,
    computed_field,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.config import project_settings
from core.core.versioning import version


current_year: int = datetime.now().year


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

    @computed_field
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
