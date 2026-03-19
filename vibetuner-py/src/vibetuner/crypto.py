# ABOUTME: Fernet encryption helpers for secrets stored in MongoDB.
# ABOUTME: Pure functions with no model or database awareness.
import base64
import re
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


FERNET_PREFIX = "gAAAAA"

_HKDF_SALT = b"vibetuner-oauth-secrets"
_HKDF_INFO = b"fernet-key"


def derive_fernet_key(passphrase: str) -> bytes:
    """Derive a 32-byte Fernet key from a passphrase using HKDF-SHA256."""
    hkdf = HKDF(
        algorithm=SHA256(),
        length=32,
        salt=_HKDF_SALT,
        info=_HKDF_INFO,
    )
    raw = hkdf.derive(passphrase.encode())
    return base64.urlsafe_b64encode(raw)


def encrypt_value(plaintext: str, passphrase: str) -> str:
    """Encrypt a plaintext string, returning a Fernet token string."""
    key = derive_fernet_key(passphrase)
    return Fernet(key).encrypt(plaintext.encode()).decode()


def decrypt_value(ciphertext: str, passphrase: str) -> str:
    """Decrypt a Fernet token string back to plaintext."""
    key = derive_fernet_key(passphrase)
    return Fernet(key).decrypt(ciphertext.encode()).decode()


def is_encrypted(value: str) -> bool:
    """Check whether a value looks like a Fernet token."""
    return value.startswith(FERNET_PREFIX)


def decrypt_or_passthrough(value: str, passphrase: str | None) -> str:
    """Decrypt if the value is encrypted, otherwise pass through.

    Raises ValueError if the value looks encrypted but no key is provided
    or decryption fails.
    """
    if not is_encrypted(value):
        return value

    if passphrase is None:
        raise ValueError(
            "Value appears encrypted but no encryption key is configured. "
            "Set FIELD_ENCRYPTION_KEY in your environment."
        )

    try:
        return decrypt_value(value, passphrase)
    except InvalidToken:
        raise ValueError(
            "Failed to decrypt value. The encryption key may be incorrect."
        ) from None


def write_env_var(env_file: Path, key: str, value: str) -> None:
    """Write or update a single variable in a .env file.

    Performs line-level find-and-replace. Creates the file if it doesn't exist.
    """
    new_line = f'{key}="{value}"'
    pattern = re.compile(rf"^{re.escape(key)}\s*=.*$", re.MULTILINE)

    if env_file.exists():
        content = env_file.read_text()
        if pattern.search(content):
            content = pattern.sub(new_line, content)
        else:
            content = content.rstrip("\n") + "\n" + new_line + "\n"
        env_file.write_text(content)
    else:
        env_file.write_text(new_line + "\n")
