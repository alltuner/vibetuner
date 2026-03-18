# ABOUTME: Tests for the OAuthAccountModel.
# ABOUTME: Covers model fields, defaults, and the app_id reference to OAuthProviderAppModel.
# ruff: noqa: S101
from unittest.mock import MagicMock

import pytest
from bson import ObjectId
from vibetuner.models.oauth import OAuthAccountModel


@pytest.fixture(autouse=True)
def mock_document_settings():
    """Allow OAuthAccountModel instantiation without MongoDB."""
    OAuthAccountModel._document_settings = MagicMock()
    yield
    OAuthAccountModel._document_settings = None


class TestOAuthAccountModel:
    def test_app_id_defaults_to_none(self):
        account = OAuthAccountModel(
            provider="google",
            provider_user_id="123",
        )
        assert account.app_id is None

    def test_app_id_accepts_object_id(self):
        oid = ObjectId()
        account = OAuthAccountModel(
            provider="google",
            provider_user_id="123",
            app_id=oid,
        )
        assert account.app_id == oid

    def test_app_id_accepts_string_as_object_id(self):
        oid = ObjectId()
        account = OAuthAccountModel(
            provider="google",
            provider_user_id="123",
            app_id=str(oid),
        )
        assert account.app_id == oid
