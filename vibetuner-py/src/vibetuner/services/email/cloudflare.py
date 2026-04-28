# ABOUTME: Cloudflare Email Service provider implementation.
# ABOUTME: Sends transactional email via Cloudflare's REST API (account-scoped).
"""Cloudflare Email Service for Agents — Python provider.

The official ``cloudflare`` SDK only added the ``email_sending.send`` resource
in ``5.0.0b2`` (a pre-release at the time of writing) and the service itself
is in public beta. Pinning a beta SDK in the blessed stack is undesirable, so
this provider talks to the documented REST endpoint directly through
``httpx.AsyncClient``. When ``cloudflare>=5.0.0`` ships stable, swapping the
implementation to the SDK is a one-file change — the inputs and JSON payload
are identical.

Endpoint:  ``POST /accounts/{account_id}/email/sending/send``
Auth:      ``Authorization: Bearer <api_token>``
Body:      ``{from, to, subject, text, html}``
"""

from typing import Any

import httpx

from vibetuner.services.email.base import EmailAddress, format_email_str


_API_BASE_URL = "https://api.cloudflare.com/client/v4"
_DEFAULT_TIMEOUT = 30.0


class CloudflareEmailProvider:
    """Email provider using Cloudflare Email Service.

    A single :class:`httpx.AsyncClient` is created lazily on first use and
    reused across requests so that connection pooling kicks in. ``aclose``
    is exposed for callers that want to release sockets explicitly (the
    framework relies on process exit otherwise, matching how the other
    providers behave).
    """

    def __init__(
        self,
        api_token: str,
        account_id: str,
        *,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> None:
        self._api_token = api_token
        self._account_id = account_id
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=_API_BASE_URL,
                timeout=self._timeout,
                headers={
                    "Authorization": f"Bearer {self._api_token}",
                    "Content-Type": "application/json",
                },
            )
        return self._client

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def send(
        self,
        from_addr: EmailAddress,
        to_addr: EmailAddress,
        subject: str,
        html_body: str,
        text_body: str,
        tags: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        # Cloudflare's documented payload does not include a tags / metadata
        # field today (public beta). The argument is accepted for protocol
        # parity — extend this once the API exposes it.
        del tags

        payload: dict[str, Any] = {
            "from": format_email_str(from_addr),
            "to": format_email_str(to_addr),
            "subject": subject,
            "text": text_body,
            "html": html_body,
        }

        client = self._get_client()
        response = await client.post(
            f"/accounts/{self._account_id}/email/sending/send",
            json=payload,
        )
        response.raise_for_status()
        return response.json()
