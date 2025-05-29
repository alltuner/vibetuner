import base64
import hashlib
from functools import cached_property

from pydantic import UUID4, BaseModel, computed_field

from ._config import project_settings, settings


class DataContext(BaseModel):
    DEBUG: bool = settings.debug

    project_name: str = project_settings.project_name
    version: str = settings.version
    copyright: str = project_settings.copyright

    default_language: str = project_settings.language
    supported_languages: set[str] = project_settings.languages

    umami_website_id: UUID4 | None = project_settings.umami_website_id

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

    model_config = {"arbitrary_types_allowed": True}


class AppContext(DataContext):
    # Add typed state here

    model_config = {"arbitrary_types_allowed": True}


data_ctx = DataContext()
ctx = AppContext()
