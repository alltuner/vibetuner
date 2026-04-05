# ABOUTME: Tests for the crypto module (Fernet encryption of OAuth secrets).
# ABOUTME: Covers key derivation, encrypt/decrypt roundtrip, detection, and .env file writing.
# ruff: noqa: S101, S105
import pytest
from vibetuner.crypto import (
    FERNET_PREFIX,
    decrypt_or_passthrough,
    decrypt_value,
    derive_fernet_key,
    encrypt_value,
    is_encrypted,
    write_env_var,
)


class TestDeriveFernetKey:
    """Key derivation must be deterministic and passphrase-sensitive."""

    def test_deterministic(self):
        key1 = derive_fernet_key("my-passphrase")
        key2 = derive_fernet_key("my-passphrase")
        assert key1 == key2

    def test_different_passphrases_produce_different_keys(self):
        key1 = derive_fernet_key("passphrase-a")
        key2 = derive_fernet_key("passphrase-b")
        assert key1 != key2

    def test_returns_bytes(self):
        key = derive_fernet_key("test")
        assert isinstance(key, bytes)

    def test_key_is_valid_fernet_key(self):
        """The derived key must be usable with Fernet directly."""
        from cryptography.fernet import Fernet

        key = derive_fernet_key("test-passphrase")
        # Should not raise
        Fernet(key)


class TestEncryptDecrypt:
    """Encrypt/decrypt roundtrip tests."""

    def test_roundtrip(self):
        passphrase = "test-key"
        plaintext = "my-secret-value"
        ciphertext = encrypt_value(plaintext, passphrase)
        assert decrypt_value(ciphertext, passphrase) == plaintext

    def test_ciphertext_differs_from_plaintext(self):
        ciphertext = encrypt_value("secret", "key")
        assert ciphertext != "secret"

    def test_ciphertext_starts_with_fernet_prefix(self):
        ciphertext = encrypt_value("secret", "key")
        assert ciphertext.startswith(FERNET_PREFIX)

    def test_wrong_key_raises(self):
        from cryptography.fernet import InvalidToken

        ciphertext = encrypt_value("secret", "correct-key")
        with pytest.raises(InvalidToken):
            decrypt_value(ciphertext, "wrong-key")

    def test_empty_string_roundtrip(self):
        ciphertext = encrypt_value("", "key")
        assert decrypt_value(ciphertext, "key") == ""


class TestIsEncrypted:
    """Detection of encrypted vs plaintext values."""

    def test_encrypted_value_detected(self):
        ciphertext = encrypt_value("secret", "key")
        assert is_encrypted(ciphertext) is True

    def test_plaintext_not_detected(self):
        assert is_encrypted("just-a-plain-secret") is False

    def test_empty_string_not_detected(self):
        assert is_encrypted("") is False

    def test_partial_prefix_not_detected(self):
        assert is_encrypted("gAAAA") is False


class TestDecryptOrPassthrough:
    """Branching logic for decrypt_or_passthrough."""

    def test_plaintext_passes_through_when_key_is_none(self):
        assert decrypt_or_passthrough("plain-secret", None) == "plain-secret"

    def test_plaintext_passes_through_when_key_is_set(self):
        assert decrypt_or_passthrough("plain-secret", "some-key") == "plain-secret"

    def test_encrypted_value_decrypted_when_key_is_correct(self):
        ciphertext = encrypt_value("secret", "my-key")
        assert decrypt_or_passthrough(ciphertext, "my-key") == "secret"

    def test_encrypted_value_without_key_passes_through(self, log_sink):
        """When no key is configured, the encrypted value passes through with a warning."""
        ciphertext = encrypt_value("secret", "my-key")
        result = decrypt_or_passthrough(ciphertext, None)
        assert result == ciphertext
        assert any("no encryption key" in m.lower() for m in log_sink)

    def test_encrypted_value_with_wrong_key_passes_through(self, log_sink):
        """When the key is wrong, the encrypted value passes through with a warning."""
        ciphertext = encrypt_value("secret", "correct-key")
        result = decrypt_or_passthrough(ciphertext, "wrong-key")
        assert result == ciphertext
        assert any("failed to decrypt" in m.lower() for m in log_sink)


class TestWriteEnvVar:
    """Tests for .env file line-level find-and-replace."""

    def test_creates_file_and_writes_var(self, tmp_path):
        env_file = tmp_path / ".env"
        write_env_var(env_file, "MY_KEY", "my-value")
        assert env_file.read_text() == 'MY_KEY="my-value"\n'

    def test_updates_existing_var(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text('MY_KEY="old-value"\nOTHER="keep"\n')
        write_env_var(env_file, "MY_KEY", "new-value")
        content = env_file.read_text()
        assert 'MY_KEY="new-value"' in content
        assert 'OTHER="keep"' in content

    def test_appends_when_var_not_present(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text('EXISTING="value"\n')
        write_env_var(env_file, "NEW_KEY", "new-value")
        content = env_file.read_text()
        assert 'EXISTING="value"' in content
        assert 'NEW_KEY="new-value"' in content

    def test_preserves_other_content(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text('# A comment\nFOO="bar"\nBAZ="qux"\n')
        write_env_var(env_file, "FOO", "updated")
        content = env_file.read_text()
        assert "# A comment" in content
        assert 'FOO="updated"' in content
        assert 'BAZ="qux"' in content

    def test_handles_unquoted_existing_value(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("MY_KEY=old-value\n")
        write_env_var(env_file, "MY_KEY", "new-value")
        content = env_file.read_text()
        assert 'MY_KEY="new-value"' in content
