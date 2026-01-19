from babel import Locale
from pydantic import UUID4, BaseModel, PrivateAttr, computed_field

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

    _locale_names_cache: dict[str, str] | None = PrivateAttr(default=None)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def locale_names(self) -> dict[str, str]:
        """Language codes mapped to native display names, sorted alphabetically."""
        if self._locale_names_cache is None:
            self._locale_names_cache = dict(
                sorted(
                    {
                        locale: (
                            Locale.parse(locale).display_name or locale
                        ).capitalize()
                        for locale in self.supported_languages
                    }.items(),
                    key=lambda x: x[1],
                ),
            )
        return self._locale_names_cache

    umami_website_id: UUID4 | None = settings.project.umami_website_id

    fqdn: str | None = settings.project.fqdn

    model_config = {"arbitrary_types_allowed": True}


ctx = Context()
