# ABOUTME: Unit tests for EmailService with multi-provider support
# ABOUTME: Tests Resend, Mailjet, and Cloudflare providers, auto-detection, and backward compat
# ruff: noqa: S101, S106

import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest


@pytest.fixture
def resend_provider():
    """Fixture for ResendEmailProvider with mocked resend module."""
    from vibetuner.services.email.resend import ResendEmailProvider

    provider = object.__new__(ResendEmailProvider)
    provider._resend = MagicMock()
    return provider


@pytest.fixture
def mailjet_provider():
    """Fixture for MailjetEmailProvider with mocked client."""
    from vibetuner.services.email.mailjet import MailjetEmailProvider

    provider = object.__new__(MailjetEmailProvider)
    provider._client = MagicMock()
    return provider


@pytest.fixture
def email_service_resend(resend_provider):
    """Fixture for EmailService using Resend provider."""
    from vibetuner.services.email import EmailService

    service = object.__new__(EmailService)
    service._provider = resend_provider
    service.from_email = "sender@example.com"
    return service


@pytest.fixture
def email_service_mailjet(mailjet_provider):
    """Fixture for EmailService using Mailjet provider."""
    from vibetuner.services.email import EmailService

    service = object.__new__(EmailService)
    service._provider = mailjet_provider
    service.from_email = "sender@example.com"
    return service


# ── ResendEmailProvider tests ────────────────────────────────────────


@pytest.mark.asyncio
async def test_resend_send_basic(resend_provider):
    """Test basic Resend send."""
    mock_result = {"id": "abc123"}

    with patch("vibetuner.services.email.resend.asyncify") as mock_asyncify:
        mock_send = AsyncMock(return_value=mock_result)
        mock_asyncify.return_value = mock_send

        result = await resend_provider.send(
            from_addr="sender@example.com",
            to_addr="recipient@example.com",
            subject="Test Subject",
            html_body="<p>Hello</p>",
            text_body="Hello",
        )

        mock_send.assert_called_once()
        call_params = mock_send.call_args[0][0]
        assert call_params["from"] == "sender@example.com"
        assert call_params["to"] == ["recipient@example.com"]
        assert call_params["subject"] == "Test Subject"
        assert call_params["html"] == "<p>Hello</p>"
        assert call_params["text"] == "Hello"
        assert "tags" not in call_params
        assert result == mock_result


@pytest.mark.asyncio
async def test_resend_send_with_tags(resend_provider):
    """Test Resend send with tags."""
    with patch("vibetuner.services.email.resend.asyncify") as mock_asyncify:
        mock_send = AsyncMock(return_value={"id": "abc123"})
        mock_asyncify.return_value = mock_send

        await resend_provider.send(
            from_addr="sender@example.com",
            to_addr="recipient@example.com",
            subject="Test",
            html_body="<p>Hi</p>",
            text_body="Hi",
            tags={"category": "welcome", "user_id": "123"},
        )

        call_params = mock_send.call_args[0][0]
        assert {"name": "category", "value": "welcome"} in call_params["tags"]
        assert {"name": "user_id", "value": "123"} in call_params["tags"]


@pytest.mark.asyncio
async def test_resend_send_named_addresses(resend_provider):
    """Test Resend send with named email addresses."""
    with patch("vibetuner.services.email.resend.asyncify") as mock_asyncify:
        mock_send = AsyncMock(return_value={"id": "abc123"})
        mock_asyncify.return_value = mock_send

        await resend_provider.send(
            from_addr=("Acme Support", "support@acme.com"),
            to_addr=("John Doe", "john@example.com"),
            subject="Test",
            html_body="<p>Hi</p>",
            text_body="Hi",
        )

        call_params = mock_send.call_args[0][0]
        assert call_params["from"] == "Acme Support <support@acme.com>"
        assert call_params["to"] == ["John Doe <john@example.com>"]


# ── MailjetEmailProvider tests ───────────────────────────────────────


@pytest.mark.asyncio
async def test_mailjet_send_basic(mailjet_provider):
    """Test basic Mailjet send."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"Messages": [{"Status": "success"}]}

    with patch("vibetuner.services.email.mailjet.asyncify") as mock_asyncify:
        mock_create = AsyncMock(return_value=mock_response)
        mock_asyncify.return_value = mock_create

        await mailjet_provider.send(
            from_addr="sender@example.com",
            to_addr="recipient@example.com",
            subject="Test Subject",
            html_body="<p>Hello</p>",
            text_body="Hello",
        )

        mock_create.assert_called_once()
        call_data = mock_create.call_args[1]["data"]
        assert call_data["Messages"][0]["From"]["Email"] == "sender@example.com"
        assert call_data["Messages"][0]["To"][0]["Email"] == "recipient@example.com"
        assert call_data["Messages"][0]["Subject"] == "Test Subject"
        assert call_data["Messages"][0]["HTMLPart"] == "<p>Hello</p>"
        assert call_data["Messages"][0]["TextPart"] == "Hello"
        assert "CustomID" not in call_data["Messages"][0]


@pytest.mark.asyncio
async def test_mailjet_send_named_addresses(mailjet_provider):
    """Test Mailjet send with named email addresses."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"Messages": [{"Status": "success"}]}

    with patch("vibetuner.services.email.mailjet.asyncify") as mock_asyncify:
        mock_create = AsyncMock(return_value=mock_response)
        mock_asyncify.return_value = mock_create

        await mailjet_provider.send(
            from_addr=("Sender Name", "sender@example.com"),
            to_addr=("Recipient Name", "recipient@example.com"),
            subject="Test",
            html_body="<p>Hi</p>",
            text_body="Hi",
        )

        call_data = mock_create.call_args[1]["data"]
        from_field = call_data["Messages"][0]["From"]
        to_field = call_data["Messages"][0]["To"][0]
        assert from_field["Email"] == "sender@example.com"
        assert from_field["Name"] == "Sender Name"
        assert to_field["Email"] == "recipient@example.com"
        assert to_field["Name"] == "Recipient Name"


@pytest.mark.asyncio
async def test_mailjet_send_with_tags(mailjet_provider):
    """Test Mailjet send maps first tag to CustomID."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"Messages": [{"Status": "success"}]}

    with patch("vibetuner.services.email.mailjet.asyncify") as mock_asyncify:
        mock_create = AsyncMock(return_value=mock_response)
        mock_asyncify.return_value = mock_create

        await mailjet_provider.send(
            from_addr="sender@example.com",
            to_addr="recipient@example.com",
            subject="Test",
            html_body="<p>Hi</p>",
            text_body="Hi",
            tags={"custom_id": "order_123"},
        )

        call_data = mock_create.call_args[1]["data"]
        assert call_data["Messages"][0]["CustomID"] == "order_123"


# ── EmailService integration tests ──────────────────────────────────


@pytest.mark.asyncio
async def test_email_service_send_basic(email_service_resend):
    """Test EmailService.send_email delegates to provider."""
    with patch("vibetuner.services.email.resend.asyncify") as mock_asyncify:
        mock_send = AsyncMock(return_value={"id": "abc123"})
        mock_asyncify.return_value = mock_send

        await email_service_resend.send_email(
            to_address="recipient@example.com",
            subject="Test Subject",
            html_body="<p>Hello</p>",
            text_body="Hello",
        )

        mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_email_service_legacy_custom_id(email_service_resend):
    """Test legacy custom_id param is passed as tag."""
    with patch("vibetuner.services.email.resend.asyncify") as mock_asyncify:
        mock_send = AsyncMock(return_value={"id": "abc123"})
        mock_asyncify.return_value = mock_send

        await email_service_resend.send_email(
            to_address="recipient@example.com",
            subject="Test",
            html_body="<p>Hi</p>",
            text_body="Hi",
            custom_id="welcome_001",
        )

        call_params = mock_send.call_args[0][0]
        assert {"name": "custom_id", "value": "welcome_001"} in call_params["tags"]


@pytest.mark.asyncio
async def test_email_service_legacy_event_payload(email_service_resend):
    """Test legacy event_payload param is passed as tag."""
    with patch("vibetuner.services.email.resend.asyncify") as mock_asyncify:
        mock_send = AsyncMock(return_value={"id": "abc123"})
        mock_asyncify.return_value = mock_send

        await email_service_resend.send_email(
            to_address="recipient@example.com",
            subject="Test",
            html_body="<p>Hi</p>",
            text_body="Hi",
            event_payload="user_id=123",
        )

        call_params = mock_send.call_args[0][0]
        assert {"name": "event_payload", "value": "user_id=123"} in call_params["tags"]


# ── CloudflareEmailProvider tests ────────────────────────────────────


def _cloudflare_provider_with_transport(handler):
    """Build a provider whose internal AsyncClient uses an httpx MockTransport."""
    from vibetuner.services.email.cloudflare import (
        _API_BASE_URL,
        CloudflareEmailProvider,
    )

    provider = CloudflareEmailProvider(api_token="cf-token", account_id="acct-xyz")
    provider._client = httpx.AsyncClient(
        base_url=_API_BASE_URL,
        transport=httpx.MockTransport(handler),
        headers={
            "Authorization": "Bearer cf-token",
            "Content-Type": "application/json",
        },
    )
    return provider


@pytest.mark.asyncio
async def test_cloudflare_send_basic_payload_and_endpoint():
    """Posts to /accounts/{id}/email/sending/send with the documented body."""
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["headers"] = dict(request.headers)
        captured["payload"] = json.loads(request.content.decode())
        return httpx.Response(
            200,
            json={
                "success": True,
                "errors": [],
                "messages": [],
                "result": {"queued": ["recipient@example.com"]},
            },
        )

    provider = _cloudflare_provider_with_transport(handler)
    try:
        result = await provider.send(
            from_addr="sender@example.com",
            to_addr="recipient@example.com",
            subject="Test Subject",
            html_body="<p>Hello</p>",
            text_body="Hello",
        )
    finally:
        await provider.aclose()

    assert captured["url"].endswith("/accounts/acct-xyz/email/sending/send")
    assert captured["headers"]["authorization"] == "Bearer cf-token"
    assert captured["payload"] == {
        "from": "sender@example.com",
        "to": "recipient@example.com",
        "subject": "Test Subject",
        "text": "Hello",
        "html": "<p>Hello</p>",
    }
    assert result["success"] is True


@pytest.mark.asyncio
async def test_cloudflare_send_named_addresses():
    """Named addresses serialise as 'Display <email>' on both sides."""
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["payload"] = json.loads(request.content.decode())
        return httpx.Response(200, json={"success": True})

    provider = _cloudflare_provider_with_transport(handler)
    try:
        await provider.send(
            from_addr=("Acme Support", "support@acme.com"),
            to_addr=("John Doe", "john@example.com"),
            subject="Test",
            html_body="<p>Hi</p>",
            text_body="Hi",
        )
    finally:
        await provider.aclose()

    assert captured["payload"]["from"] == "Acme Support <support@acme.com>"
    assert captured["payload"]["to"] == "John Doe <john@example.com>"


@pytest.mark.asyncio
async def test_cloudflare_send_ignores_tags():
    """Tags are accepted for protocol parity but not yet sent (API has no field)."""
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["payload"] = json.loads(request.content.decode())
        return httpx.Response(200, json={"success": True})

    provider = _cloudflare_provider_with_transport(handler)
    try:
        await provider.send(
            from_addr="sender@example.com",
            to_addr="recipient@example.com",
            subject="Test",
            html_body="<p>Hi</p>",
            text_body="Hi",
            tags={"category": "welcome"},
        )
    finally:
        await provider.aclose()

    # Body matches the documented schema exactly — no extra fields leaked.
    assert set(captured["payload"]) == {"from", "to", "subject", "text", "html"}


@pytest.mark.asyncio
async def test_cloudflare_send_raises_on_4xx():
    """Non-2xx responses surface as httpx.HTTPStatusError."""

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, json={"errors": [{"message": "Auth failed"}]})

    provider = _cloudflare_provider_with_transport(handler)
    try:
        with pytest.raises(httpx.HTTPStatusError) as exc:
            await provider.send(
                from_addr="sender@example.com",
                to_addr="recipient@example.com",
                subject="Test",
                html_body="<p>Hi</p>",
                text_body="Hi",
            )
    finally:
        await provider.aclose()

    assert exc.value.response.status_code == 403


@pytest.mark.asyncio
async def test_cloudflare_aclose_idempotent():
    """Calling aclose twice doesn't raise; client is reset to None."""
    from vibetuner.services.email.cloudflare import CloudflareEmailProvider

    provider = CloudflareEmailProvider(api_token="cf-token", account_id="acct-xyz")
    # Force lazy client creation.
    provider._get_client()
    assert provider._client is not None
    await provider.aclose()
    assert provider._client is None
    await provider.aclose()  # second call is a no-op


# ── _resolve_provider auto-detection tests ───────────────────────────


def _patch_mail_settings(**kwargs):
    """Return a context manager that swaps ``settings.mail`` with the given values."""
    fake = MagicMock()
    fake.provider = kwargs.get("provider")
    for attr in (
        "resend_api_key",
        "mailjet_api_key",
        "mailjet_api_secret",
        "cloudflare_api_token",
        "cloudflare_account_id",
    ):
        fake.__setattr__(attr, kwargs.get(attr))
    return patch("vibetuner.services.email.service.settings.mail", fake)


def _secret(value: str):
    sec = MagicMock()
    sec.get_secret_value.return_value = value
    sec.__bool__ = lambda self: True
    return sec


def test_resolve_auto_detect_cloudflare_when_token_and_account_set():
    from vibetuner.services.email.cloudflare import CloudflareEmailProvider
    from vibetuner.services.email.service import _resolve_provider

    with _patch_mail_settings(
        cloudflare_api_token=_secret("cf-token"),
        cloudflare_account_id="acct-xyz",
    ):
        provider = _resolve_provider()
    assert isinstance(provider, CloudflareEmailProvider)


def test_resolve_explicit_cloudflare_provider_requires_both_credentials():
    from vibetuner.services.email.base import EmailServiceNotConfiguredError
    from vibetuner.services.email.service import _resolve_provider

    # Missing account id
    with (
        _patch_mail_settings(
            provider="cloudflare", cloudflare_api_token=_secret("cf-token")
        ),
        pytest.raises(EmailServiceNotConfiguredError),
    ):
        _resolve_provider()

    # Missing token
    with (
        _patch_mail_settings(provider="cloudflare", cloudflare_account_id="acct-xyz"),
        pytest.raises(EmailServiceNotConfiguredError),
    ):
        _resolve_provider()


def test_resolve_resend_wins_over_cloudflare_when_both_configured():
    """Auto-detection priority: resend > mailjet > cloudflare."""
    from vibetuner.services.email.resend import ResendEmailProvider
    from vibetuner.services.email.service import _resolve_provider

    with _patch_mail_settings(
        resend_api_key=_secret("re_xxx"),
        cloudflare_api_token=_secret("cf-token"),
        cloudflare_account_id="acct-xyz",
    ):
        provider = _resolve_provider()
    assert isinstance(provider, ResendEmailProvider)
