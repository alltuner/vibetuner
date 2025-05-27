from typing import Any

from pydantic import BaseModel

from ._config import __project_name__, __version__, settings


def get_copyright() -> str:
    if (
        settings.copyright_start is not None
        and settings.copyright_start != settings.copyright_current
    ):
        year_string = f"{settings.copyright_start}-{settings.copyright_current}"
    else:
        year_string = str(settings.copyright_current)

    if settings.company_name is not None:
        return f"© {year_string} {settings.company_name}"
    else:
        return f"© {year_string}"


class AppContext(BaseModel):
    project_name: str = __project_name__
    version: str = __version__
    copyright: str = get_copyright()
    DEBUG: bool = settings.debug

    umami_website_id: str = settings.umami_website_id

    # Add typed state here

    model_config = {"arbitrary_types_allowed": True}


ctx = AppContext()
ctx_dict: dict[str, Any] = AppContext().model_dump()
