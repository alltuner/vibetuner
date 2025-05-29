from pydantic import UUID4, BaseModel

from ._config import project_settings, settings


class DataContext(BaseModel):
    DEBUG: bool = settings.debug

    project_name: str = project_settings.project_name

    version: str = settings.version
    v_hash: str = settings.v_hash

    copyright: str = project_settings.copyright

    default_language: str = project_settings.language
    supported_languages: set[str] = project_settings.languages

    umami_website_id: UUID4 | None = project_settings.umami_website_id

    model_config = {"arbitrary_types_allowed": True}


class AppContext(DataContext):
    # Add typed state here

    model_config = {"arbitrary_types_allowed": True}


data_ctx = DataContext()
ctx = AppContext()
