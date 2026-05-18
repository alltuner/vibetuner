# ABOUTME: Tests user_edit_submit handler's language preference handling
# ABOUTME: Validates the fix for #1862 - empty submission clears language back to auto-detect
# ruff: noqa: S101

"""
Tests for user_edit_submit endpoint language handling.

Mocks UserModel.get and the user's save() method so we can exercise the
handler logic directly without a running database. Asserts that:
- empty-string language clears the preference back to None (auto-detect)
- a supported language code is stored as LanguageAlpha2
- an unsupported language code leaves the existing preference untouched
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic_extra_types.language_code import LanguageAlpha2
from starlette.authentication import AuthCredentials, SimpleUser
from starlette.requests import Request


class _AuthedUser(SimpleUser):
    """SimpleUser variant with an .id attribute matching UserModel access."""

    def __init__(self, user_id: str) -> None:
        super().__init__(username=user_id)
        self.id = user_id

    @property
    def is_authenticated(self) -> bool:
        return True


def _make_request(user_id: str = "u1") -> Request:
    """Build a minimal authenticated Request with session and user.id."""
    scope: dict = {
        "type": "http",
        "method": "POST",
        "path": "/user/edit",
        "headers": [],
        "session": {},
        "auth": AuthCredentials(["authenticated"]),
        "user": _AuthedUser(user_id),
    }
    return Request(scope)


def _make_user(language: LanguageAlpha2 | None = None) -> MagicMock:
    """Build a UserModel stub with user_settings.language and async save()."""
    from vibetuner.models.user import UserModel, UserSettings

    user = MagicMock(spec=UserModel)
    user.user_settings = UserSettings(language=language)
    user.name = "Original"
    user.session_dict = {"id": "u1", "settings": {}}
    user.save = AsyncMock()
    return user


@pytest.mark.asyncio
async def test_empty_language_clears_preference():
    """Submitting language='' resets user_settings.language to None."""
    from vibetuner.frontend.routes.user import user_edit_submit

    user = _make_user(language=LanguageAlpha2("ca"))
    request = _make_request()

    with (
        patch(
            "vibetuner.frontend.routes.user.UserModel.get",
            new=AsyncMock(return_value=user),
        ),
        patch(
            "vibetuner.frontend.routes.user.ctx.supported_languages",
            new={"en", "ca", "es"},
        ),
    ):
        await user_edit_submit(request, name="New Name", language="")

    assert user.user_settings.language is None
    assert user.name == "New Name"
    user.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_supported_language_is_saved():
    """Submitting a supported code stores it as LanguageAlpha2."""
    from vibetuner.frontend.routes.user import user_edit_submit

    user = _make_user(language=None)
    request = _make_request()

    with (
        patch(
            "vibetuner.frontend.routes.user.UserModel.get",
            new=AsyncMock(return_value=user),
        ),
        patch(
            "vibetuner.frontend.routes.user.ctx.supported_languages",
            new={"en", "ca", "es"},
        ),
    ):
        await user_edit_submit(request, name="New Name", language="ca")

    assert user.user_settings.language == LanguageAlpha2("ca")
    user.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_unsupported_language_is_ignored():
    """Submitting an unsupported code leaves the existing preference intact."""
    from vibetuner.frontend.routes.user import user_edit_submit

    user = _make_user(language=LanguageAlpha2("ca"))
    request = _make_request()

    with (
        patch(
            "vibetuner.frontend.routes.user.UserModel.get",
            new=AsyncMock(return_value=user),
        ),
        patch(
            "vibetuner.frontend.routes.user.ctx.supported_languages",
            new={"en", "ca", "es"},
        ),
    ):
        await user_edit_submit(request, name="New Name", language="xx")

    assert user.user_settings.language == LanguageAlpha2("ca")
    user.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_none_language_leaves_preference_unchanged():
    """When no language field is submitted (None), preference is not touched."""
    from vibetuner.frontend.routes.user import user_edit_submit

    user = _make_user(language=LanguageAlpha2("ca"))
    request = _make_request()

    with (
        patch(
            "vibetuner.frontend.routes.user.UserModel.get",
            new=AsyncMock(return_value=user),
        ),
        patch(
            "vibetuner.frontend.routes.user.ctx.supported_languages",
            new={"en", "ca", "es"},
        ),
    ):
        await user_edit_submit(request, name="New Name", language=None)

    assert user.user_settings.language == LanguageAlpha2("ca")
    user.save.assert_awaited_once()
