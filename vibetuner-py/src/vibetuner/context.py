from pydantic import UUID4, BaseModel

from vibetuner.config import settings


class Context(BaseModel):
    DEBUG: bool = settings.debug

    project_name: str = settings.project.project_name
    project_slug: str = settings.project.project_slug
    project_description: str = settings.project.project_description

    version: str = settings.version
    v_hash: str = settings.v_hash

    copyright: str = settings.project.copyright

    default_language: str = settings.project.language
    supported_languages: set[str] = settings.project.languages

    umami_website_id: UUID4 | None = settings.project.umami_website_id

    fqdn: str | None = settings.project.fqdn

    model_config = {"arbitrary_types_allowed": True}
