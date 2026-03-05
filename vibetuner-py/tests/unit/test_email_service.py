# ABOUTME: Unit tests for EmailService with multi-provider support
# ABOUTME: Tests Resend and Mailjet providers, auto-detection, and backward compat
# ruff: noqa: S101

from unittest.mock import AsyncMock, MagicMock, patch

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
