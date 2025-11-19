"""Email service for sending transactional emails via AWS SES.

WARNING: This is a scaffolding-managed file. DO NOT MODIFY directly.
To extend email functionality, create wrapper services in the parent services directory.
"""

from typing import Literal

import aioboto3

from vibetuner.config import settings


SES_SERVICE_NAME: Literal["ses"] = "ses"


class SESEmailService:
    def __init__(
        self,
        from_email: str | None = None,
    ) -> None:
        self.session = aioboto3.Session(
            region_name=settings.project.aws_default_region,
            aws_access_key_id=settings.aws_access_key_id.get_secret_value()
            if settings.aws_access_key_id
            else None,
            aws_secret_access_key=settings.aws_secret_access_key.get_secret_value()
            if settings.aws_secret_access_key
            else None,
        )
        self.from_email = from_email or settings.project.from_email

    async def send_email(
        self, to_address: str, subject: str, html_body: str, text_body: str
    ):
        """Send email using Amazon SES"""
        async with self.session.client(SES_SERVICE_NAME) as ses_client:
            response = await ses_client.send_email(
                Source=self.from_email,
                Destination={"ToAddresses": [to_address]},
                Message={
                    "Subject": {"Data": subject, "Charset": "UTF-8"},
                    "Body": {
                        "Html": {"Data": html_body, "Charset": "UTF-8"},
                        "Text": {"Data": text_body, "Charset": "UTF-8"},
                    },
                },
            )
            return response
