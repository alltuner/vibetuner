# ABOUTME: Resend email provider implementation.
# ABOUTME: Sends transactional emails via the Resend API.

from typing import TYPE_CHECKING, Any, cast

from asyncer import asyncify

from vibetuner.logging import logger
from vibetuner.services.email.base import EmailAddress, format_email_str


if TYPE_CHECKING:
    from resend.emails._emails import Emails as _ResendEmails


# Resend's per-send rate-limit and quota signals. Informational on a successful
# send and populated on a RateLimitError; the rest of the response headers carry
# nothing relevant to limit observability.
_RATE_LIMIT_HEADERS = (
    "ratelimit-limit",
    "ratelimit-remaining",
    "ratelimit-reset",
    "ratelimit-policy",
    "x-resend-monthly-quota",
)


def _rate_limit_info(headers: dict[str, str] | None) -> dict[str, str]:
    """Pick the rate-limit/quota headers out of a Resend response."""
    if not headers:
        return {}
    return {key: headers[key] for key in _RATE_LIMIT_HEADERS if key in headers}


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
        from resend.exceptions import RateLimitError

        params: dict[str, Any] = {
            "from": format_email_str(from_addr),
            "to": [format_email_str(to_addr)],
            "subject": subject,
            "html": html_body,
            "text": text_body,
        }
        if tags:
            params["tags"] = [{"name": k, "value": v} for k, v in tags.items()]
        send_params = cast("_ResendEmails.SendParams", params)
        try:
            result = await asyncify(self._resend.Emails.send)(send_params)
        except RateLimitError as exc:
            logger.warning(
                "Resend rate limit hit ({}): {}",
                exc.error_type,
                _rate_limit_info(exc.headers),
            )
            raise
        result_dict = dict(result)
        info = _rate_limit_info(
            cast("dict[str, str] | None", result_dict.get("http_headers"))
        )
        if info:
            logger.debug("Resend rate limit status: {}", info)
        return result_dict
