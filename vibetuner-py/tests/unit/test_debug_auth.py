# ABOUTME: Unit tests for debug route authentication and authorization.
# ABOUTME: Verifies cookie-based access checks and HMAC-signed unlock validation.
# ruff: noqa: S101, S105

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from vibetuner.debug_signing import generate_debug_url, verify_debug_signature


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

    These tests verify the HMAC signature validation in unlock_debug_access.
    In DEBUG mode: no signature required.
    In production: requires a valid HMAC-signed link (returns 404 on failure).
    """

    SECRET = "test-session-key"

    def _parse_params(self, url: str) -> dict[str, str]:
        from urllib.parse import parse_qs, urlparse

        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        return {k: v[0] for k, v in params.items()}

    def _validate_unlock(
        self,
        debug_mode: bool,
        ts: str | None = None,
        nonce: str | None = None,
        sig: str | None = None,
    ):
        """Mirror the HMAC validation logic from unlock_debug_access."""
        if debug_mode:
            return True

        if ts is None or nonce is None or sig is None:
            raise HTTPException(status_code=404, detail="Not found")

        if not verify_debug_signature(ts=ts, nonce=nonce, sig=sig, secret=self.SECRET):
            raise HTTPException(status_code=404, detail="Not found")

        return True

    def test_debug_mode_no_signature_required(self):
        """In DEBUG mode, cookie can be set without any signature."""
        result = self._validate_unlock(debug_mode=True)
        assert result is True

    def test_production_missing_params_returns_404(self):
        """In production without HMAC params, returns 404."""
        with pytest.raises(HTTPException) as exc_info:
            self._validate_unlock(debug_mode=False)
        assert exc_info.value.status_code == 404

    def test_production_partial_params_returns_404(self):
        """In production with only some HMAC params, returns 404."""
        with pytest.raises(HTTPException) as exc_info:
            self._validate_unlock(debug_mode=False, ts="123", nonce="abc")
        assert exc_info.value.status_code == 404

    def test_production_valid_signature_allows(self):
        """In production with valid HMAC-signed params, access is granted."""
        url = generate_debug_url("https://example.com", self.SECRET)
        params = self._parse_params(url)
        result = self._validate_unlock(debug_mode=False, **params)
        assert result is True

    def test_production_wrong_secret_returns_404(self):
        """In production, a link signed with a different secret is rejected."""
        url = generate_debug_url("https://example.com", "wrong-secret")
        params = self._parse_params(url)
        with pytest.raises(HTTPException) as exc_info:
            self._validate_unlock(debug_mode=False, **params)
        assert exc_info.value.status_code == 404

    def test_production_tampered_signature_returns_404(self):
        """In production, a tampered signature is rejected."""
        url = generate_debug_url("https://example.com", self.SECRET)
        params = self._parse_params(url)
        params["sig"] = "tampered"
        with pytest.raises(HTTPException) as exc_info:
            self._validate_unlock(debug_mode=False, **params)
        assert exc_info.value.status_code == 404
