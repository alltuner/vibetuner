# ABOUTME: Tests for at-rest encryption of secret config entries.
# ABOUTME: Validates that ConfigEntryModel encrypts secret_value via EncryptedFieldsMixin.
# ruff: noqa: S101, S105, S106

import json
from typing import Any

from pydantic import Field
from vibetuner.config import settings
from vibetuner.crypto import encrypt_value, is_encrypted
from vibetuner.models.config_entry import ConfigEntryModel, ConfigValueType
from vibetuner.models.mixins import EncryptedFieldsMixin, EncryptedStr


PASSPHRASE = "test-encryption-key"


class FakeConfigEntry(EncryptedFieldsMixin):
    """Mirrors ConfigEntryModel fields without requiring Beanie initialization."""

    key: str = Field(default="test.key")
    value: Any = Field(default=None)
    value_type: ConfigValueType = Field(default="str")
    is_secret: bool = Field(default=False)
    secret_value: EncryptedStr | None = Field(default=None)

    @property
    def effective_value(self) -> Any:
        """Return the real value, deserializing from secret_value when needed."""
        if self.secret_value is not None:
            return json.loads(self.secret_value)
        return self.value


class TestConfigEntryModelShape:
    """Tests that ConfigEntryModel has the expected fields and mixins."""

    def test_has_secret_value_field(self):
        """ConfigEntryModel has a secret_value field."""
        assert "secret_value" in ConfigEntryModel.model_fields

    def test_has_encrypted_fields_mixin(self):
        """ConfigEntryModel uses EncryptedFieldsMixin."""
        assert issubclass(ConfigEntryModel, EncryptedFieldsMixin)


class TestConfigEntryEncryption:
    """Tests for encrypting secret config values at rest."""

    def test_non_secret_entry_has_no_secret_value(self):
        """Non-secret entries store value normally with secret_value=None."""
        entry = FakeConfigEntry(key="app.name", value="my-app", value_type="str")
        assert entry.value == "my-app"
        assert entry.secret_value is None

    def test_secret_value_encrypted_on_insert(self, monkeypatch):
        """secret_value is encrypted before database insert."""
        monkeypatch.setattr(settings, "field_encryption_key", PASSPHRASE)
        entry = FakeConfigEntry(
            key="api.key",
            value=None,
            value_type="str",
            is_secret=True,
            secret_value="super-secret-key",
        )
        entry.encrypt_on_insert()
        assert is_encrypted(entry.secret_value)

    def test_secret_value_decrypted_on_load(self, monkeypatch):
        """secret_value is decrypted when loading from database."""
        monkeypatch.setattr(settings, "field_encryption_key", PASSPHRASE)
        ciphertext = encrypt_value("super-secret-key", PASSPHRASE)
        entry = FakeConfigEntry(
            key="api.key",
            value=None,
            value_type="str",
            is_secret=True,
            secret_value=ciphertext,
        )
        assert entry.secret_value == "super-secret-key"

    def test_secret_value_none_when_not_secret(self, monkeypatch):
        """Non-secret entries leave secret_value as None after encryption."""
        monkeypatch.setattr(settings, "field_encryption_key", PASSPHRASE)
        entry = FakeConfigEntry(
            key="app.name", value="my-app", value_type="str", is_secret=False
        )
        entry.encrypt_on_insert()
        assert entry.secret_value is None
        assert entry.value == "my-app"

    def test_no_encryption_when_key_unset(self, monkeypatch):
        """secret_value stays plaintext when no encryption key is configured."""
        monkeypatch.setattr(settings, "field_encryption_key", None)
        entry = FakeConfigEntry(
            key="api.key",
            value=None,
            value_type="str",
            is_secret=True,
            secret_value="plain-secret",
        )
        entry.encrypt_on_insert()
        assert entry.secret_value == "plain-secret"


class TestEffectiveValue:
    """Tests for the effective_value property."""

    def test_returns_secret_value_when_secret(self, monkeypatch):
        """effective_value returns deserialized secret_value for secret entries."""
        monkeypatch.setattr(settings, "field_encryption_key", PASSPHRASE)
        entry = FakeConfigEntry(
            key="api.key",
            value=None,
            value_type="str",
            is_secret=True,
            secret_value=json.dumps("super-secret"),
        )
        assert entry.effective_value == "super-secret"

    def test_returns_value_when_not_secret(self):
        """effective_value returns value for non-secret entries."""
        entry = FakeConfigEntry(key="app.name", value="my-app", value_type="str")
        assert entry.effective_value == "my-app"

    def test_deserializes_int(self, monkeypatch):
        """effective_value deserializes JSON integer from secret_value."""
        monkeypatch.setattr(settings, "field_encryption_key", PASSPHRASE)
        entry = FakeConfigEntry(
            key="api.max_retries",
            value=None,
            value_type="int",
            is_secret=True,
            secret_value=json.dumps(42),
        )
        assert entry.effective_value == 42

    def test_deserializes_bool(self, monkeypatch):
        """effective_value deserializes JSON boolean from secret_value."""
        monkeypatch.setattr(settings, "field_encryption_key", PASSPHRASE)
        entry = FakeConfigEntry(
            key="api.enabled",
            value=None,
            value_type="bool",
            is_secret=True,
            secret_value=json.dumps(True),
        )
        assert entry.effective_value is True

    def test_deserializes_json(self, monkeypatch):
        """effective_value deserializes JSON object from secret_value."""
        monkeypatch.setattr(settings, "field_encryption_key", PASSPHRASE)
        data = {"host": "example.com", "port": 443}
        entry = FakeConfigEntry(
            key="api.config",
            value=None,
            value_type="json",
            is_secret=True,
            secret_value=json.dumps(data),
        )
        assert entry.effective_value == data
