from pydantic import UUID4, BaseModel

from .config import project_settings, settings


class Context(BaseModel):
    DEBUG: bool = settings.debug

    project_name: str = project_settings.project_name
    project_slug: str = project_settings.project_slug
    project_description: str = project_settings.project_description

    version: str = settings.version
    v_hash: str = settings.v_hash

    copyright: str = project_settings.copyright

    default_language: str = project_settings.language
    supported_languages: set[str] = project_settings.languages

    umami_website_id: UUID4 | None = project_settings.umami_website_id

    fqdn: str | None = project_settings.fqdn

    model_config = {"arbitrary_types_allowed": True}
