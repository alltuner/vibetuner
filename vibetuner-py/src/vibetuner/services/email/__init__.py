# ABOUTME: Email service package with multi-provider support.
# ABOUTME: Re-exports public API for backward-compatible imports.

from vibetuner.services.email.base import (
    EmailAddress,
    EmailProvider,
    EmailServiceNotConfiguredError,
)
from vibetuner.services.email.mailjet import MailjetEmailProvider
from vibetuner.services.email.resend import ResendEmailProvider
from vibetuner.services.email.service import EmailService


__all__ = [
    "EmailAddress",
    "EmailProvider",
    "EmailService",
    "EmailServiceNotConfiguredError",
    "MailjetEmailProvider",
    "ResendEmailProvider",
]
