# ABOUTME: Unit tests for EmailService.send_email method
# ABOUTME: Tests CustomID and EventPayload traceability parameters for Mailjet
# ruff: noqa: S101

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def email_service():
    """Fixture for EmailService with mocked client, bypassing __init__."""
    from vibetuner.services.email import EmailService

    # Create instance without calling __init__ to avoid settings validation
    service = object.__new__(EmailService)
    service.client = MagicMock()
    service.from_email = "sender@example.com"
    return service


@pytest.mark.asyncio
async def test_send_email_basic(email_service):
    """Test basic send_email without traceability params."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"Messages": [{"Status": "success"}]}

    with patch("vibetuner.services.email.asyncify") as mock_asyncify:
        mock_create = AsyncMock(return_value=mock_response)
        mock_asyncify.return_value = mock_create

        await email_service.send_email(
            to_address="recipient@example.com",
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
        assert "EventPayload" not in call_data["Messages"][0]


@pytest.mark.asyncio
async def test_send_email_with_custom_id(email_service):
    """Test send_email with custom_id for message correlation."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"Messages": [{"Status": "success"}]}

    with patch("vibetuner.services.email.asyncify") as mock_asyncify:
        mock_create = AsyncMock(return_value=mock_response)
        mock_asyncify.return_value = mock_create

        await email_service.send_email(
            to_address="recipient@example.com",
            subject="Test",
            html_body="<p>Hi</p>",
            text_body="Hi",
            custom_id="welcome_email_001",
        )

        call_data = mock_create.call_args[1]["data"]
        assert call_data["Messages"][0]["CustomID"] == "welcome_email_001"


@pytest.mark.asyncio
async def test_send_email_with_event_payload(email_service):
    """Test send_email with event_payload for webhook metadata."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"Messages": [{"Status": "success"}]}

    with patch("vibetuner.services.email.asyncify") as mock_asyncify:
        mock_create = AsyncMock(return_value=mock_response)
        mock_asyncify.return_value = mock_create

        await email_service.send_email(
            to_address="recipient@example.com",
            subject="Test",
            html_body="<p>Hi</p>",
            text_body="Hi",
            event_payload="user_id=123,action=signup",
        )

        call_data = mock_create.call_args[1]["data"]
        assert call_data["Messages"][0]["EventPayload"] == "user_id=123,action=signup"


@pytest.mark.asyncio
async def test_send_email_with_both_traceability_params(email_service):
    """Test send_email with both custom_id and event_payload."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"Messages": [{"Status": "success"}]}

    with patch("vibetuner.services.email.asyncify") as mock_asyncify:
        mock_create = AsyncMock(return_value=mock_response)
        mock_asyncify.return_value = mock_create

        await email_service.send_email(
            to_address="recipient@example.com",
            subject="Test",
            html_body="<p>Hi</p>",
            text_body="Hi",
            custom_id="order_confirmation_456",
            event_payload='{"order_id": 456, "total": 99.99}',
        )

        call_data = mock_create.call_args[1]["data"]
        assert call_data["Messages"][0]["CustomID"] == "order_confirmation_456"
        assert (
            call_data["Messages"][0]["EventPayload"]
            == '{"order_id": 456, "total": 99.99}'
        )
