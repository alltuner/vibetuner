# ABOUTME: Regression tests for WebUser session validation and AuthBackend logging.
# ABOUTME: Guards against silent logout when a session user lacks an optional `name` (#1873).
# ruff: noqa: S101

import pytest
from starlette.requests import HTTPConnection
from vibetuner.frontend.middleware import AuthBackend
from vibetuner.frontend.oauth import WebUser


def test_webuser_accepts_session_without_name():
    """A user impersonated/loaded from session_dict that omits `name` is still valid."""
    user = WebUser.model_validate(
        {"id": "u1", "email": "ada@example.com", "settings": {}}
    )
    assert user.name is None
    assert user.is_authenticated is True


def test_webuser_display_name_falls_back_to_email_prefix():
    """display_name falls back to the email local-part when name is missing."""
    user = WebUser(id="u1", email="ada@example.com")
    assert user.display_name == "ada"


def test_webuser_display_name_prefers_name_when_present():
    user = WebUser(id="u1", name="Ada Lovelace", email="ada@example.com")
    assert user.display_name == "Ada Lovelace"


def _make_conn_with_session_user(user_data: object) -> HTTPConnection:
    scope: dict = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [],
        "session": {"user": user_data},
    }
    return HTTPConnection(scope)


@pytest.mark.asyncio
async def test_auth_backend_authenticates_nameless_session_user():
    """A session dict without `name` no longer triggers a silent logout."""
    conn = _make_conn_with_session_user(
        {"id": "u1", "email": "ada@example.com", "settings": {}}
    )

    result = await AuthBackend().authenticate(conn)

    assert result is not None
    credentials, user = result
    assert "authenticated" in credentials.scopes
    assert isinstance(user, WebUser)
    assert user.id == "u1"
    assert conn.session.get("user") == {
        "id": "u1",
        "email": "ada@example.com",
        "settings": {},
    }


@pytest.mark.asyncio
async def test_auth_backend_logs_warning_when_session_invalid(log_sink):
    """When session data really is malformed, we log a warning instead of failing silently."""
    conn = _make_conn_with_session_user({"id": "u1"})  # missing required `email`

    result = await AuthBackend().authenticate(conn)

    assert result is None
    assert "user" not in conn.session
    assert any(
        "Clearing invalid session user data" in message for message in log_sink
    ), log_sink
