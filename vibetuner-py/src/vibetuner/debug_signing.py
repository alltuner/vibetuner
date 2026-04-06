# ABOUTME: HMAC-SHA256 signed URL generation and verification for debug access.
# ABOUTME: Pure functions with no framework dependencies, used by both CLI and server.

import hashlib
import hmac
import secrets
import time
from urllib.parse import urlencode


def generate_debug_url(base_url: str, secret: str) -> str:
    """Generate a short-lived HMAC-signed URL for debug access."""
    base_url = base_url.rstrip("/")
    ts = str(int(time.time()))
    nonce = secrets.token_hex(16)
    sig = _sign(ts, nonce, secret)
    params = urlencode({"ts": ts, "nonce": nonce, "sig": sig})
    return f"{base_url}/_unlock-debug?{params}"


def verify_debug_signature(
    ts: str, nonce: str, sig: str, secret: str, ttl: int = 300
) -> bool:
    """Verify an HMAC-signed debug link. Returns False on any invalid input."""
    try:
        expected = _sign(ts, nonce, secret)
        if not hmac.compare_digest(sig, expected):
            return False
        if time.time() - int(ts) > ttl:
            return False
    except (ValueError, TypeError):
        return False
    return True


def _sign(ts: str, nonce: str, secret: str) -> str:
    message = f"{ts}:{nonce}"
    return hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
