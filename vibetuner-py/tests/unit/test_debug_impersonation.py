# ABOUTME: Tests debug impersonation routes preserve the admin's session.
# ABOUTME: Regression coverage for #1875 (stop-impersonation must restore, not clear).
# ruff: noqa: S101

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from starlette.requests import Request
from vibetuner.frontend.routes import debug as debug_routes


@pytest.fixture(autouse=True)
def _force_debug_mode(monkeypatch):
    """Impersonation routes are 404 unless ctx.DEBUG is true."""
    monkeypatch.setattr(debug_routes.ctx, "DEBUG", True)


def _make_request(session: dict | None = None) -> Request:
    scope: dict = {
        "type": "http",
        "method": "POST",
        "path": "/debug/impersonate",
        "headers": [],
        "session": session if session is not None else {},
    }
    return Request(scope)


def _make_user(user_id: str, session_dict: dict) -> MagicMock:
    user = MagicMock()
    user.id = user_id
    user.session_dict = session_dict
    return user


@pytest.mark.asyncio
async def test_impersonate_stashes_original_user():
    admin = {"id": "admin1", "email": "admin@example.com", "settings": {}}
    target_dict = {"id": "u2", "email": "u2@example.com", "settings": {}}
    request = _make_request(session={"user": dict(admin)})

    target = _make_user("u2", target_dict)
    with patch.object(
        debug_routes.UserModel, "get", new=AsyncMock(return_value=target)
    ):
        await debug_routes.debug_impersonate_user(request, "u2")

    assert request.session["user"] == target_dict
    assert request.session["original_user"] == admin


@pytest.mark.asyncio
async def test_stop_impersonation_restores_original_user():
    admin = {"id": "admin1", "email": "admin@example.com", "settings": {}}
    target = {"id": "u2", "email": "u2@example.com", "settings": {}}
    request = _make_request(session={"user": target, "original_user": admin})

    await debug_routes.debug_stop_impersonation(request)

    assert request.session["user"] == admin
    assert "original_user" not in request.session


@pytest.mark.asyncio
async def test_stop_impersonation_clears_session_when_no_original():
    """Without an original_user (admin somehow lacked a session), keep old behaviour."""
    request = _make_request(session={"user": {"id": "u2", "email": "u2@example.com"}})

    await debug_routes.debug_stop_impersonation(request)

    assert "user" not in request.session
    assert "original_user" not in request.session


@pytest.mark.asyncio
async def test_chained_impersonations_preserve_root_admin():
    """Hopping admin -> u2 -> u3 -> stop must return to the root admin, not u2."""
    admin = {"id": "admin1", "email": "admin@example.com", "settings": {}}
    u2_dict = {"id": "u2", "email": "u2@example.com", "settings": {}}
    u3_dict = {"id": "u3", "email": "u3@example.com", "settings": {}}
    request = _make_request(session={"user": dict(admin)})

    with patch.object(
        debug_routes.UserModel,
        "get",
        new=AsyncMock(
            side_effect=[_make_user("u2", u2_dict), _make_user("u3", u3_dict)]
        ),
    ):
        await debug_routes.debug_impersonate_user(request, "u2")
        await debug_routes.debug_impersonate_user(request, "u3")

    assert request.session["user"] == u3_dict
    assert request.session["original_user"] == admin

    await debug_routes.debug_stop_impersonation(request)

    assert request.session["user"] == admin
    assert "original_user" not in request.session


@pytest.mark.asyncio
async def test_impersonate_without_existing_session_does_not_stash():
    """Calling impersonate while logged out shouldn't synthesise an original_user."""
    target_dict = {"id": "u2", "email": "u2@example.com", "settings": {}}
    request = _make_request(session={})

    target = _make_user("u2", target_dict)
    with patch.object(
        debug_routes.UserModel, "get", new=AsyncMock(return_value=target)
    ):
        await debug_routes.debug_impersonate_user(request, "u2")

    assert request.session["user"] == target_dict
    assert "original_user" not in request.session
