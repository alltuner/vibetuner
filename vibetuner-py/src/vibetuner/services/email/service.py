# ABOUTME: EmailService facade and provider resolution.
# ABOUTME: Resolves the configured provider and delegates email sending.

from collections.abc import Callable
from typing import Any, NoReturn

from vibetuner.config import MailSettings, settings
from vibetuner.services.email.base import (
    EmailAddress,
    EmailProvider,
    EmailServiceNotConfiguredError,
)


def _raise_not_configured() -> NoReturn:
    from vibetuner.services.errors import email_not_configured

    raise EmailServiceNotConfiguredError(email_not_configured(log=False))


def _build_resend(mail: MailSettings) -> EmailProvider:
    if not mail.resend_api_key:
        _raise_not_configured()
    from vibetuner.services.email.resend import ResendEmailProvider

    return ResendEmailProvider(api_key=mail.resend_api_key.get_secret_value())


def _build_mailjet(mail: MailSettings) -> EmailProvider:
    if not mail.mailjet_api_key or not mail.mailjet_api_secret:
        _raise_not_configured()
    from vibetuner.services.email.mailjet import MailjetEmailProvider

    return MailjetEmailProvider(
        api_key=mail.mailjet_api_key.get_secret_value(),
        api_secret=mail.mailjet_api_secret.get_secret_value(),
    )


def _build_cloudflare(mail: MailSettings) -> EmailProvider:
    if not mail.cloudflare_api_token or not mail.cloudflare_account_id:
        _raise_not_configured()
    from vibetuner.services.email.cloudflare import CloudflareEmailProvider

    return CloudflareEmailProvider(
        api_token=mail.cloudflare_api_token.get_secret_value(),
        account_id=mail.cloudflare_account_id,
    )


# Order defines auto-detection priority when MAIL_PROVIDER is unset.
# Each entry is (name, predicate, builder). Adding a new provider is a single
# entry plus its build_* helper.
_PROVIDERS: list[
    tuple[
        str,
        Callable[[MailSettings], bool],
        Callable[[MailSettings], EmailProvider],
    ]
] = [
    ("resend", lambda m: bool(m.resend_api_key), _build_resend),
    (
        "mailjet",
        lambda m: bool(m.mailjet_api_key and m.mailjet_api_secret),
        _build_mailjet,
    ),
    (
        "cloudflare",
        lambda m: bool(m.cloudflare_api_token and m.cloudflare_account_id),
        _build_cloudflare,
    ),
]


def configured_provider() -> str | None:
    """Return the configured email provider name, or ``None`` if not set.

    Resolution mirrors :func:`_resolve_provider`: an explicit ``MAIL_PROVIDER``
    wins, otherwise the registry's first entry whose predicate matches is
    selected. The provider's credentials must satisfy its predicate to count
    as configured — if ``MAIL_PROVIDER`` names a provider but its credentials
    are missing, this returns ``None`` rather than the bare name.

    Useful for health checks and capability reporting that need to know
    whether email sending is wired up without paying the cost of importing
    the provider's SDK.
    """
    mail = settings.mail
    explicit = mail.provider
    for candidate, predicate, _ in _PROVIDERS:
        if explicit is None:
            if predicate(mail):
                return candidate
        elif candidate == explicit and predicate(mail):
            return candidate
    return None


def _resolve_provider() -> EmailProvider:
    """Resolve the email provider from settings."""
    mail = settings.mail
    explicit = mail.provider

    if explicit is not None:
        for candidate, _, builder in _PROVIDERS:
            if candidate == explicit:
                return builder(mail)
        _raise_not_configured()

    for _candidate, predicate, builder in _PROVIDERS:
        if predicate(mail):
            return builder(mail)

    _raise_not_configured()


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
