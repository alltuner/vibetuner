# ABOUTME: Base types and protocol for email providers.
# ABOUTME: Defines EmailAddress, EmailProvider protocol, and shared helpers.

from typing import Any, Protocol, runtime_checkable


# Named email: ("Display Name", "email@example.com") or just "email@example.com"
EmailAddress = str | tuple[str, str]


class EmailServiceNotConfiguredError(Exception):
    """Raised when email service credentials are not configured."""


@runtime_checkable
class EmailProvider(Protocol):
    """Protocol for email sending providers."""

    async def send(
        self,
        from_addr: EmailAddress,
        to_addr: EmailAddress,
        subject: str,
        html_body: str,
        text_body: str,
        tags: dict[str, str] | None = None,
    ) -> dict[str, Any]: ...


def format_email_str(addr: EmailAddress) -> str:
    """Format an EmailAddress as 'Name <email>' or plain email string."""
    if isinstance(addr, str):
        return addr
    name, email = addr
    return f"{name} <{email}>"
