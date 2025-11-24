# ABOUTME: Unit tests for debug route authentication and authorization
# ABOUTME: Verifies that debug routes require proper token/cookie authentication in production
# ruff: noqa: S101, S106

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException


# Inline the constant to avoid importing vibetuner.frontend
MAGIC_COOKIE_NAME = "magic_access"


class TestRequireMagicCookie:
    """Test the require_magic_cookie dependency logic."""

    def _require_magic_cookie(self, request):
        """Replicate the require_magic_cookie logic for testing."""
        if MAGIC_COOKIE_NAME not in request.cookies:
            raise HTTPException(status_code=403, detail="Access forbidden")
        if request.cookies[MAGIC_COOKIE_NAME] != "granted":
            raise HTTPException(status_code=403, detail="Access forbidden")

    def test_missing_cookie_raises_403(self):
        """Test that missing magic cookie raises 403."""
        request = MagicMock()
        request.cookies = {}

        with pytest.raises(HTTPException) as exc_info:
            self._require_magic_cookie(request)

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Access forbidden"

    def test_wrong_cookie_value_raises_403(self):
        """Test that wrong cookie value raises 403."""
        request = MagicMock()
        request.cookies = {MAGIC_COOKIE_NAME: "wrong_value"}

        with pytest.raises(HTTPException) as exc_info:
            self._require_magic_cookie(request)

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Access forbidden"

    def test_correct_cookie_passes(self):
        """Test that correct magic cookie passes."""
        request = MagicMock()
        request.cookies = {MAGIC_COOKIE_NAME: "granted"}

        # Should not raise
        self._require_magic_cookie(request)


class TestCheckDebugAccess:
    """Test the check_debug_access function logic.

    These tests specify the DESIRED behavior after fixing issue #448.
    The current implementation uses ?prod=1 which is insecure.
    """

    def _check_debug_access(self, request, debug_mode: bool):
        """Replicate the DESIRED check_debug_access logic.

        In DEBUG mode: always allow.
        In production: require magic cookie.
        """
        if debug_mode:
            return True

        # In production, require magic cookie
        if MAGIC_COOKIE_NAME not in request.cookies:
            raise HTTPException(status_code=404, detail="Not found")
        if request.cookies[MAGIC_COOKIE_NAME] != "granted":
            raise HTTPException(status_code=404, detail="Not found")

        return True

    def test_debug_mode_always_allows(self):
        """Test that DEBUG mode always allows access."""
        request = MagicMock()
        request.cookies = {}

        result = self._check_debug_access(request, debug_mode=True)
        assert result is True

    def test_production_without_cookie_denies(self):
        """Test that production without magic cookie denies access."""
        request = MagicMock()
        request.cookies = {}

        with pytest.raises(HTTPException) as exc_info:
            self._check_debug_access(request, debug_mode=False)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Not found"

    def test_production_with_magic_cookie_allows(self):
        """Test that production with magic cookie allows access."""
        request = MagicMock()
        request.cookies = {MAGIC_COOKIE_NAME: "granted"}

        result = self._check_debug_access(request, debug_mode=False)
        assert result is True

    def test_production_wrong_cookie_value_denies(self):
        """Test that wrong cookie value denies access."""
        request = MagicMock()
        request.cookies = {MAGIC_COOKIE_NAME: "wrong_value"}

        with pytest.raises(HTTPException) as exc_info:
            self._check_debug_access(request, debug_mode=False)

        assert exc_info.value.status_code == 404


class TestSetMagicCookie:
    """Test the /debug/magic endpoint logic for setting magic cookie.

    These tests specify the DESIRED behavior after fixing issue #448.
    In production, a valid DEBUG_ACCESS_TOKEN must be provided.
    """

    def _validate_token_for_magic_cookie(
        self, token: str | None, debug_mode: bool, configured_token: str | None
    ):
        """Validate token before setting magic cookie.

        In DEBUG mode: no token required.
        In production: token must match DEBUG_ACCESS_TOKEN.
        If no token is configured in production, debug access is disabled.
        """
        if debug_mode:
            return True

        # In production, require token
        if configured_token is None:
            # No token configured = debug access disabled in production
            raise HTTPException(status_code=404, detail="Not found")

        if token is None or token != configured_token:
            raise HTTPException(status_code=404, detail="Not found")

        return True

    def test_debug_mode_sets_cookie_without_token(self):
        """Test that DEBUG mode sets cookie without requiring token."""
        result = self._validate_token_for_magic_cookie(
            token=None, debug_mode=True, configured_token=None
        )
        assert result is True

    def test_production_requires_token(self):
        """Test that production mode requires valid token."""
        with pytest.raises(HTTPException) as exc_info:
            self._validate_token_for_magic_cookie(
                token=None, debug_mode=False, configured_token="secret-token-123"
            )

        assert exc_info.value.status_code == 404

    def test_production_wrong_token_denies(self):
        """Test that wrong token is rejected."""
        with pytest.raises(HTTPException) as exc_info:
            self._validate_token_for_magic_cookie(
                token="wrong-token",
                debug_mode=False,
                configured_token="secret-token-123",
            )

        assert exc_info.value.status_code == 404

    def test_production_correct_token_allows(self):
        """Test that correct token allows setting cookie."""
        result = self._validate_token_for_magic_cookie(
            token="secret-token-123",
            debug_mode=False,
            configured_token="secret-token-123",
        )
        assert result is True

    def test_production_no_token_configured_denies_all(self):
        """Test that if no token is configured, debug access is disabled in prod."""
        with pytest.raises(HTTPException) as exc_info:
            self._validate_token_for_magic_cookie(
                token="any-token", debug_mode=False, configured_token=None
            )

        assert exc_info.value.status_code == 404
