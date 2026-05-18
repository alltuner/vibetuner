# ABOUTME: Tests user_edit_submit handler's language preference handling
# ABOUTME: Validates fixes for #1862 (clear branch) and #1870 (Form default empty string)
# ruff: noqa: S101

"""
Tests for user_edit_submit endpoint language handling.

Mocks UserModel.get and the user's save() method so we can exercise the
handler logic directly without a running database. Asserts that:
- empty-string language clears the preference back to None (auto-detect)
- a supported language code is stored as LanguageAlpha2
- an unsupported language code leaves the existing preference untouched

Also includes a TestClient regression test that exercises FastAPI's form
parsing to prove an empty submission reaches the handler as "" (not None),
which is the contract the clear branch depends on.
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


def test_form_default_empty_string_passes_through_fastapi():
    """Regression for #1870.

    The user_edit_submit handler relies on an empty `language` form value reaching
    its body so the `if language == ""` branch can clear the preference. FastAPI
    coerces empty form values to the parameter default, so the default must be ""
    (not None). This test pins that contract: with Form(""), both an empty value
    and an omitted field arrive as "".
    """
    from fastapi import FastAPI, Form
    from fastapi.testclient import TestClient

    app = FastAPI()

    @app.post("/probe")
    async def probe(language: str = Form("")) -> dict[str, str]:
        return {"language": language}

    client = TestClient(app)
    assert client.post("/probe", data={"language": ""}).json() == {"language": ""}
    assert client.post("/probe", data={}).json() == {"language": ""}


def test_user_edit_submit_language_form_default_is_empty_string():
    """Lock in the Form default itself in case the handler signature is touched.

    Pairs with test_form_default_empty_string_passes_through_fastapi: that test
    proves "" survives FastAPI parsing, this one proves the handler still asks
    for "".
    """
    import inspect

    from fastapi.params import Form as FormParam
    from vibetuner.frontend.routes.user import user_edit_submit

    language_param = inspect.signature(user_edit_submit).parameters["language"]
    default = language_param.default
    assert isinstance(default, FormParam)
    assert default.default == ""
