# ABOUTME: Resend email provider implementation.
# ABOUTME: Sends transactional emails via the Resend API.

from typing import Any

from asyncer import asyncify

from vibetuner.services.email.base import EmailAddress, format_email_str


class ResendEmailProvider:
    """Email provider using Resend API."""

    def __init__(self, api_key: str) -> None:
        import resend

        resend.api_key = api_key
        self._resend = resend

    async def send(
        self,
        from_addr: EmailAddress,
        to_addr: EmailAddress,
        subject: str,
        html_body: str,
        text_body: str,
        tags: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "from": format_email_str(from_addr),
            "to": [format_email_str(to_addr)],
            "subject": subject,
            "html": html_body,
            "text": text_body,
        }
        if tags:
            params["tags"] = [{"name": k, "value": v} for k, v in tags.items()]
        result = await asyncify(self._resend.Emails.send)(params)
        return result
