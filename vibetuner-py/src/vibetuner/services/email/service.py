# ABOUTME: EmailService facade and provider resolution.
# ABOUTME: Resolves the configured provider and delegates email sending.

from typing import Any

from vibetuner.config import settings
from vibetuner.services.email.base import (
    EmailAddress,
    EmailProvider,
    EmailServiceNotConfiguredError,
)


def _resolve_provider() -> EmailProvider:
    """Resolve the email provider from settings."""
    mail = settings.mail

    # Explicit provider selection
    provider = mail.provider

    # Auto-detect from available credentials
    if provider is None:
        if mail.resend_api_key:
            provider = "resend"
        elif mail.mailjet_api_key and mail.mailjet_api_secret:
            provider = "mailjet"

    if provider == "resend":
        if not mail.resend_api_key:
            from vibetuner.services.errors import email_not_configured

            raise EmailServiceNotConfiguredError(email_not_configured(log=False))
        from vibetuner.services.email.resend import ResendEmailProvider

        return ResendEmailProvider(api_key=mail.resend_api_key.get_secret_value())

    if provider == "mailjet":
        if not mail.mailjet_api_key or not mail.mailjet_api_secret:
            from vibetuner.services.errors import email_not_configured

            raise EmailServiceNotConfiguredError(email_not_configured(log=False))
        from vibetuner.services.email.mailjet import MailjetEmailProvider

        return MailjetEmailProvider(
            api_key=mail.mailjet_api_key.get_secret_value(),
            api_secret=mail.mailjet_api_secret.get_secret_value(),
        )

    from vibetuner.services.errors import email_not_configured

    raise EmailServiceNotConfiguredError(email_not_configured(log=False))


class EmailService:
    def __init__(self, from_email: EmailAddress | None = None) -> None:
        self._provider = _resolve_provider()
        self.from_email = from_email or settings.project.from_email

    async def send_email(
        self,
        to_address: EmailAddress,
        subject: str,
        html_body: str,
        text_body: str,
        custom_id: str | None = None,
        event_payload: str | None = None,
        tags: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        # Build tags from legacy params + explicit tags
        merged_tags = dict(tags) if tags else {}
        if custom_id is not None:
            merged_tags["custom_id"] = custom_id
        if event_payload is not None:
            merged_tags["event_payload"] = event_payload

        return await self._provider.send(
            from_addr=self.from_email,
            to_addr=to_address,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            tags=merged_tags or None,
        )
