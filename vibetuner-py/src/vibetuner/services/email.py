# ABOUTME: Email service for sending transactional emails via Mailjet.
# ABOUTME: Provides MailjetEmailService class with async send_email method.

from typing import Any

from asyncer import asyncify
from mailjet_rest import Client

from vibetuner.config import settings


# Named email: ("Display Name", "email@example.com") or just "email@example.com"
EmailAddress = str | tuple[str, str]


def _format_email_address(addr: EmailAddress) -> dict[str, str]:
    """Convert email address to Mailjet format."""
    if isinstance(addr, str):
        return {"Email": addr}
    name, email = addr
    return {"Email": email, "Name": name}


class EmailServiceNotConfiguredError(Exception):
    """Raised when email service credentials are not configured."""


class EmailService:
    def __init__(self, from_email: EmailAddress | None = None) -> None:
        if not settings.mailjet_api_key or not settings.mailjet_api_secret:
            from vibetuner.services.errors import email_not_configured

            raise EmailServiceNotConfiguredError(email_not_configured(log=False))
        self.client = Client(
            auth=(
                settings.mailjet_api_key.get_secret_value(),
                settings.mailjet_api_secret.get_secret_value(),
            ),
            version="v3.1",
        )
        self.from_email = from_email or settings.project.from_email

    async def send_email(
        self,
        to_address: EmailAddress,
        subject: str,
        html_body: str,
        text_body: str,
        custom_id: str | None = None,
        event_payload: str | None = None,
    ) -> dict[str, Any]:
        message: dict[str, Any] = {
            "From": _format_email_address(self.from_email),
            "To": [_format_email_address(to_address)],
            "Subject": subject,
            "HTMLPart": html_body,
            "TextPart": text_body,
        }
        if custom_id is not None:
            message["CustomID"] = custom_id
        if event_payload is not None:
            message["EventPayload"] = event_payload
        data = {"Messages": [message]}
        result = await asyncify(self.client.send.create)(data=data)
        return result.json()
