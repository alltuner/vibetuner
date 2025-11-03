from pydantic import EmailStr
from starlette_babel import gettext_lazy as _

from vibetuner.config import settings
from vibetuner.services.email import SESEmailService

from .templates import render_static_template


async def send_magic_link_email(
    ses_service: SESEmailService,
    lang: str,
    to_address: EmailStr,
    login_url: str,
) -> None:
    project_name = settings.project.project_name

    html_body = render_static_template(
        "magic_link.html",
        namespace="email",
        lang=lang,
        context={
            "login_url": str(login_url),
            "project_name": project_name,
        },
    )

    text_body = render_static_template(
        "magic_link.txt",
        namespace="email",
        lang=lang,
        context={
            "login_url": str(login_url),
            "project_name": project_name,
        },
    )

    await ses_service.send_email(
        subject=_("Sign in to {project_name}").format(
            project_name=settings.project.project_name
        ),
        html_body=html_body,
        text_body=text_body,
        to_address=to_address,
    )
