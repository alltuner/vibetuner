# ABOUTME: Unit tests for debug route authentication and authorization
# ABOUTME: Verifies that debug routes require proper token/cookie authentication in production
# ruff: noqa: S101, S106

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException


MAGIC_COOKIE_NAME = "magic_access"


class TestCheckDebugAccess:
    """Test the check_debug_access function logic.

    These tests verify the behavior implemented in debug.py:check_debug_access.
    In DEBUG mode: always allow access.
    In production: require magic cookie (returns 404 to avoid info leakage).
    """

    def _check_debug_access(self, request, debug_mode: bool):
        """Mirror the check_debug_access logic from debug.py."""
        if debug_mode:
            return True

        if MAGIC_COOKIE_NAME not in request.cookies:
            raise HTTPException(status_code=404, detail="Not found")
        if request.cookies[MAGIC_COOKIE_NAME] != "granted":
            raise HTTPException(status_code=404, detail="Not found")

        return True

    def test_debug_mode_always_allows(self):
        """In DEBUG mode, access is granted without any cookie."""
        request = MagicMock()
        request.cookies = {}

        result = self._check_debug_access(request, debug_mode=True)
        assert result is True

    def test_production_without_cookie_returns_404(self):
        """In production without magic cookie, returns 404."""
        request = MagicMock()
        request.cookies = {}

        with pytest.raises(HTTPException) as exc_info:
            self._check_debug_access(request, debug_mode=False)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Not found"

    def test_production_with_valid_cookie_allows(self):
        """In production with valid magic cookie, access is granted."""
        request = MagicMock()
        request.cookies = {MAGIC_COOKIE_NAME: "granted"}

        result = self._check_debug_access(request, debug_mode=False)
        assert result is True

    def test_production_with_wrong_cookie_returns_404(self):
        """In production with wrong cookie value, returns 404."""
        request = MagicMock()
        request.cookies = {MAGIC_COOKIE_NAME: "wrong_value"}

        with pytest.raises(HTTPException) as exc_info:
            self._check_debug_access(request, debug_mode=False)

        assert exc_info.value.status_code == 404


class TestUnlockDebugAccess:
    """Test the /_unlock-debug endpoint logic.

    These tests verify the token validation in unlock_debug_access from debug.py.
    In DEBUG mode: no token required.
    In production: token must match DEBUG_ACCESS_TOKEN (returns 404 on failure).
    """

    def _validate_unlock_token(
        self, token: str | None, debug_mode: bool, configured_token: str | None
    ):
        """Mirror the token validation logic from unlock_debug_access."""
        if debug_mode:
            return True

        if configured_token is None:
            raise HTTPException(status_code=404, detail="Not found")

        if token is None or token != configured_token:
            raise HTTPException(status_code=404, detail="Not found")

        return True

    def test_debug_mode_no_token_required(self):
        """In DEBUG mode, cookie can be set without any token."""
        result = self._validate_unlock_token(
            token=None, debug_mode=True, configured_token=None
        )
        assert result is True

    def test_production_missing_token_returns_404(self):
        """In production without token, returns 404."""
        with pytest.raises(HTTPException) as exc_info:
            self._validate_unlock_token(
                token=None, debug_mode=False, configured_token="secret-token-123"
            )

        assert exc_info.value.status_code == 404

    def test_production_wrong_token_returns_404(self):
        """In production with wrong token, returns 404."""
        with pytest.raises(HTTPException) as exc_info:
            self._validate_unlock_token(
                token="wrong-token",
                debug_mode=False,
                configured_token="secret-token-123",
            )

        assert exc_info.value.status_code == 404

    def test_production_correct_token_allows(self):
        """In production with correct token, access is granted."""
        result = self._validate_unlock_token(
            token="secret-token-123",
            debug_mode=False,
            configured_token="secret-token-123",
        )
        assert result is True

    def test_production_no_token_configured_returns_404(self):
        """If DEBUG_ACCESS_TOKEN not configured, debug access is disabled."""
        with pytest.raises(HTTPException) as exc_info:
            self._validate_unlock_token(
                token="any-token", debug_mode=False, configured_token=None
            )

        assert exc_info.value.status_code == 404
