from typing import Any

from castuner.core.http import get_http_client
from castuner.scheduler.jobs import JobPool
from castuner.search.service import SearchClient
from httpx import AsyncClient
from pydantic import BaseModel
from redis.asyncio import Redis

from ._config import __version__, project_settings, settings


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
    DEBUG: bool = settings.debug

    project_name: str = project_settings.project_name
    version: str = __version__
    copyright: str = get_copyright()

    default_language: str = project_settings.language
    supported_languages: set[str] = project_settings.languages

    session_key: str = settings.session_key

    umami_website_id: str = project_settings.umami_website_id

    # Add typed state here
    http: AsyncClient = get_http_client()
    solr: SearchClient = SearchClient()
    jobpool: JobPool = JobPool()
    redis: Redis = Redis.from_url(str(settings.redis_url))

    model_config = {"arbitrary_types_allowed": True}


ctx = AppContext()
ctx_dict: dict[str, Any] = AppContext().model_dump()
