# ABOUTME: Mailjet email provider implementation.
# ABOUTME: Sends transactional emails via the Mailjet REST API.

from typing import Any

from asyncer import asyncify

from vibetuner.services.email.base import EmailAddress


def _format_email_mailjet(addr: EmailAddress) -> dict[str, str]:
    """Convert email address to Mailjet format."""
    if isinstance(addr, str):
        return {"Email": addr}
    name, email = addr
    return {"Email": email, "Name": name}


class MailjetEmailProvider:
    """Email provider using Mailjet API."""

    def __init__(self, api_key: str, api_secret: str) -> None:
        from mailjet_rest import Client

        self._client = Client(auth=(api_key, api_secret), version="v3.1")

    async def send(
        self,
        from_addr: EmailAddress,
        to_addr: EmailAddress,
        subject: str,
        html_body: str,
        text_body: str,
        tags: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        message: dict[str, Any] = {
            "From": _format_email_mailjet(from_addr),
            "To": [_format_email_mailjet(to_addr)],
            "Subject": subject,
            "HTMLPart": html_body,
            "TextPart": text_body,
        }
        if tags:
            tag_items = list(tags.items())
            # First tag maps to CustomID for backward compatibility
            message["CustomID"] = tag_items[0][1]
            if len(tag_items) > 1:
                import json

                message["EventPayload"] = json.dumps(dict(tag_items[1:]))
        data = {"Messages": [message]}
        result = await asyncify(self._client.send.create)(data=data)
        return result.json()
