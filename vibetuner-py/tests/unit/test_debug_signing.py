# ABOUTME: Tests for the HMAC-signed debug link generation and verification.
# ABOUTME: Covers roundtrip signing, expiry, tampered inputs, and malformed data.
# ruff: noqa: S101, S106, S107

from unittest.mock import patch

import pytest
from vibetuner.debug_signing import generate_debug_url, verify_debug_signature


class TestGenerateDebugUrl:
    def test_returns_url_with_expected_params(self):
        url = generate_debug_url("https://myapp.com", "mysecret")
        assert url.startswith("https://myapp.com/_unlock-debug?")
        assert "ts=" in url
        assert "nonce=" in url
        assert "sig=" in url

    def test_strips_trailing_slash_from_base_url(self):
        url = generate_debug_url("https://myapp.com/", "mysecret")
        assert "myapp.com//_unlock-debug" not in url
        assert "myapp.com/_unlock-debug" in url


class TestVerifyDebugSignature:
    def _generate_params(self, secret: str = "mysecret") -> dict[str, str]:
        """Generate valid params by parsing a generated URL."""
        from urllib.parse import parse_qs, urlparse

        url = generate_debug_url("https://example.com", secret)
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        return {
            "ts": params["ts"][0],
            "nonce": params["nonce"][0],
            "sig": params["sig"][0],
        }

    def test_roundtrip_valid(self):
        params = self._generate_params("mysecret")
        assert verify_debug_signature(**params, secret="mysecret") is True

    def test_wrong_secret_rejected(self):
        params = self._generate_params("mysecret")
        assert verify_debug_signature(**params, secret="wrongsecret") is False

    def test_expired_timestamp_rejected(self):
        params = self._generate_params("mysecret")
        # Simulate 6 minutes later (TTL is 5 minutes = 300s)
        future_time = float(params["ts"]) + 360
        with patch("vibetuner.debug_signing.time") as mock_time:
            mock_time.time.return_value = future_time
            assert verify_debug_signature(**params, secret="mysecret") is False

    def test_within_ttl_accepted(self):
        params = self._generate_params("mysecret")
        # Simulate 4 minutes later (within 5 minute TTL)
        future_time = float(params["ts"]) + 240
        with patch("vibetuner.debug_signing.time") as mock_time:
            mock_time.time.return_value = future_time
            assert verify_debug_signature(**params, secret="mysecret") is True

    def test_custom_ttl(self):
        params = self._generate_params("mysecret")
        future_time = float(params["ts"]) + 120
        with patch("vibetuner.debug_signing.time") as mock_time:
            mock_time.time.return_value = future_time
            # 60s TTL should reject a 120s old link
            assert (
                verify_debug_signature(**params, secret="mysecret", ttl=60) is False
            )

    def test_tampered_nonce_rejected(self):
        params = self._generate_params("mysecret")
        params["nonce"] = "tampered"
        assert verify_debug_signature(**params, secret="mysecret") is False

    def test_tampered_timestamp_rejected(self):
        params = self._generate_params("mysecret")
        params["ts"] = str(int(params["ts"]) + 1)
        assert verify_debug_signature(**params, secret="mysecret") is False

    def test_tampered_signature_rejected(self):
        params = self._generate_params("mysecret")
        params["sig"] = "deadbeef" * 8
        assert verify_debug_signature(**params, secret="mysecret") is False

    @pytest.mark.parametrize(
        "ts,nonce,sig",
        [
            ("notanumber", "abc", "def"),
            ("", "", ""),
            ("123", "abc", ""),
        ],
    )
    def test_malformed_input_returns_false(self, ts: str, nonce: str, sig: str):
        assert verify_debug_signature(ts=ts, nonce=nonce, sig=sig, secret="s") is False
