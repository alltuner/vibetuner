# ABOUTME: Unit tests for vibetuner.models.mixins module.
# ABOUTME: Tests TimeStampMixin and EncryptedFieldsMixin functionality.
# ruff: noqa: S101, S105, S106

from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest
from pydantic import Field
from vibetuner.config import settings
from vibetuner.models.mixins import (
    EncryptedFieldsMixin,
    EncryptedStr,
    Since,
    TimeStampMixin,
    _encrypted_field_names,
)
from vibetuner.time import Unit


class TestSince:
    """Test the Since enum."""

    def test_since_values(self):
        """Test that Since enum has correct string values."""
        assert Since.CREATION == "creation"
        assert Since.UPDATE == "update"


class SampleModel(TimeStampMixin):
    """Sample model for TimeStampMixin tests."""

    name: str = "test"


class TestTimeStampMixin:
    """Test the TimeStampMixin class."""

    def test_default_timestamps(self):
        """Test that default timestamps are set on model instantiation."""
        doc = SampleModel()
        assert isinstance(doc.db_insert_dt, datetime)
        assert isinstance(doc.db_update_dt, datetime)
        assert doc.db_insert_dt.tzinfo == UTC
        assert doc.db_update_dt.tzinfo == UTC

    def test_timestamps_equal_on_creation(self):
        """Test that insert and update timestamps are equal on creation."""
        doc = SampleModel()
        # Timestamps should be very close (within a second)
        assert abs((doc.db_insert_dt - doc.db_update_dt).total_seconds()) < 1

    @patch("vibetuner.models.mixins.now")
    def test_touch_on_insert(self, mock_now):
        """Test that _touch_on_insert sets both timestamps."""
        fixed_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = fixed_time

        doc = SampleModel()
        doc._touch_on_insert()

        assert doc.db_insert_dt == fixed_time
        assert doc.db_update_dt == fixed_time

    @patch("vibetuner.models.mixins.now")
    def test_touch_on_update(self, mock_now):
        """Test that _touch_on_update only updates db_update_dt."""
        insert_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        update_time = datetime(2025, 1, 15, 13, 0, 0, tzinfo=UTC)

        # Create doc with fixed insert time
        mock_now.return_value = insert_time
        doc = SampleModel()
        doc._touch_on_insert()

        # Update with different time
        mock_now.return_value = update_time
        doc._touch_on_update()

        assert doc.db_insert_dt == insert_time  # Should not change
        assert doc.db_update_dt == update_time  # Should be updated

    @patch("vibetuner.models.mixins.now")
    def test_age_since_creation(self, mock_now):
        """Test age() calculation since creation."""
        insert_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        current_time = datetime(2025, 1, 15, 14, 0, 0, tzinfo=UTC)  # 2 hours later

        # Create doc
        mock_now.return_value = insert_time
        doc = SampleModel()
        doc._touch_on_insert()

        # Calculate age
        mock_now.return_value = current_time
        age = doc.age(since=Since.CREATION)

        assert isinstance(age, timedelta)
        assert age == timedelta(hours=2)

    @patch("vibetuner.models.mixins.now")
    def test_age_since_update(self, mock_now):
        """Test age() calculation since last update."""
        insert_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        update_time = datetime(2025, 1, 15, 13, 0, 0, tzinfo=UTC)
        current_time = datetime(2025, 1, 15, 14, 0, 0, tzinfo=UTC)

        # Create and update doc
        mock_now.return_value = insert_time
        doc = SampleModel()
        doc._touch_on_insert()

        mock_now.return_value = update_time
        doc._touch_on_update()

        # Calculate age since update
        mock_now.return_value = current_time
        age = doc.age(since=Since.UPDATE)

        assert age == timedelta(hours=1)  # 1 hour since update

    @patch("vibetuner.models.mixins.now")
    def test_age_default_since_creation(self, mock_now):
        """Test that age() defaults to Since.CREATION."""
        insert_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        current_time = datetime(2025, 1, 15, 15, 0, 0, tzinfo=UTC)

        mock_now.return_value = insert_time
        doc = SampleModel()
        doc._touch_on_insert()

        mock_now.return_value = current_time
        age = doc.age()  # No 'since' parameter

        assert age == timedelta(hours=3)

    @patch("vibetuner.models.mixins.now")
    def test_age_in_seconds(self, mock_now):
        """Test age_in() with seconds unit."""
        insert_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        current_time = datetime(
            2025, 1, 15, 12, 5, 30, tzinfo=UTC
        )  # 5 min 30 sec later

        mock_now.return_value = insert_time
        doc = SampleModel()
        doc._touch_on_insert()

        mock_now.return_value = current_time
        age = doc.age_in(Unit.SECONDS)

        assert age == 330.0  # 5 * 60 + 30

    @patch("vibetuner.models.mixins.now")
    def test_age_in_minutes(self, mock_now):
        """Test age_in() with minutes unit."""
        insert_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        current_time = datetime(2025, 1, 15, 13, 30, 0, tzinfo=UTC)  # 1.5 hours later

        mock_now.return_value = insert_time
        doc = SampleModel()
        doc._touch_on_insert()

        mock_now.return_value = current_time
        age = doc.age_in(Unit.MINUTES)

        assert age == 90.0  # 1.5 hours = 90 minutes

    @patch("vibetuner.models.mixins.now")
    def test_age_in_hours(self, mock_now):
        """Test age_in() with hours unit."""
        insert_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        current_time = datetime(2025, 1, 15, 18, 0, 0, tzinfo=UTC)  # 6 hours later

        mock_now.return_value = insert_time
        doc = SampleModel()
        doc._touch_on_insert()

        mock_now.return_value = current_time
        age = doc.age_in(Unit.HOURS)

        assert age == 6.0

    @patch("vibetuner.models.mixins.now")
    def test_age_in_days(self, mock_now):
        """Test age_in() with days unit."""
        insert_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        current_time = datetime(2025, 1, 18, 12, 0, 0, tzinfo=UTC)  # 3 days later

        mock_now.return_value = insert_time
        doc = SampleModel()
        doc._touch_on_insert()

        mock_now.return_value = current_time
        age = doc.age_in(Unit.DAYS)

        assert age == 3.0

    @patch("vibetuner.models.mixins.now")
    def test_age_in_weeks(self, mock_now):
        """Test age_in() with weeks unit."""
        insert_time = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)  # 2 weeks later

        mock_now.return_value = insert_time
        doc = SampleModel()
        doc._touch_on_insert()

        mock_now.return_value = current_time
        age = doc.age_in(Unit.WEEKS)

        assert age == 2.0

    @patch("vibetuner.models.mixins.now")
    def test_age_in_default_seconds(self, mock_now):
        """Test that age_in() defaults to seconds."""
        insert_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        current_time = datetime(2025, 1, 15, 12, 1, 0, tzinfo=UTC)  # 1 minute later

        mock_now.return_value = insert_time
        doc = SampleModel()
        doc._touch_on_insert()

        mock_now.return_value = current_time
        age = doc.age_in()  # No unit parameter

        assert age == 60.0

    @patch("vibetuner.models.mixins.now")
    def test_age_in_with_since_update(self, mock_now):
        """Test age_in() with since=UPDATE parameter."""
        insert_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        update_time = datetime(2025, 1, 15, 13, 0, 0, tzinfo=UTC)
        current_time = datetime(2025, 1, 15, 13, 30, 0, tzinfo=UTC)

        mock_now.return_value = insert_time
        doc = SampleModel()
        doc._touch_on_insert()

        mock_now.return_value = update_time
        doc._touch_on_update()

        mock_now.return_value = current_time
        age = doc.age_in(Unit.MINUTES, since=Since.UPDATE)

        assert age == 30.0  # 30 minutes since update

    @patch("vibetuner.models.mixins.now")
    def test_is_older_than_true(self, mock_now):
        """Test is_older_than() returns True when document is older."""
        insert_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        current_time = datetime(2025, 1, 15, 14, 0, 0, tzinfo=UTC)  # 2 hours later

        mock_now.return_value = insert_time
        doc = SampleModel()
        doc._touch_on_insert()

        mock_now.return_value = current_time
        is_older = doc.is_older_than(timedelta(hours=1))

        assert is_older is True

    @patch("vibetuner.models.mixins.now")
    def test_is_older_than_false(self, mock_now):
        """Test is_older_than() returns False when document is younger."""
        insert_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        current_time = datetime(2025, 1, 15, 12, 30, 0, tzinfo=UTC)  # 30 minutes later

        mock_now.return_value = insert_time
        doc = SampleModel()
        doc._touch_on_insert()

        mock_now.return_value = current_time
        is_older = doc.is_older_than(timedelta(hours=1))

        assert is_older is False

    @patch("vibetuner.models.mixins.now")
    def test_is_older_than_exact_age(self, mock_now):
        """Test is_older_than() returns True when age exactly equals delta."""
        insert_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        current_time = datetime(
            2025, 1, 15, 13, 0, 0, tzinfo=UTC
        )  # Exactly 1 hour later

        mock_now.return_value = insert_time
        doc = SampleModel()
        doc._touch_on_insert()

        mock_now.return_value = current_time
        is_older = doc.is_older_than(timedelta(hours=1))

        assert is_older is True  # >= comparison

    @patch("vibetuner.models.mixins.now")
    def test_is_older_than_with_since_update(self, mock_now):
        """Test is_older_than() with since=UPDATE parameter."""
        insert_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        update_time = datetime(2025, 1, 15, 13, 0, 0, tzinfo=UTC)
        current_time = datetime(2025, 1, 15, 13, 30, 0, tzinfo=UTC)

        mock_now.return_value = insert_time
        doc = SampleModel()
        doc._touch_on_insert()

        mock_now.return_value = update_time
        doc._touch_on_update()

        mock_now.return_value = current_time
        is_older = doc.is_older_than(timedelta(minutes=20), since=Since.UPDATE)

        assert is_older is True  # 30 minutes > 20 minutes

    @patch("vibetuner.models.mixins.now")
    def test_touch_method(self, mock_now):
        """Test touch() method updates db_update_dt."""
        insert_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        touch_time = datetime(2025, 1, 15, 13, 0, 0, tzinfo=UTC)

        mock_now.return_value = insert_time
        doc = SampleModel()
        doc._touch_on_insert()

        mock_now.return_value = touch_time
        result = doc.touch()

        assert doc.db_update_dt == touch_time
        assert doc.db_insert_dt == insert_time  # Should not change
        assert result is doc  # Should return self for chaining

    @patch("vibetuner.models.mixins.now")
    def test_touch_method_chaining(self, mock_now):
        """Test that touch() can be chained."""
        insert_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        touch_time = datetime(2025, 1, 15, 13, 0, 0, tzinfo=UTC)

        mock_now.return_value = insert_time
        doc = SampleModel()
        doc._touch_on_insert()

        mock_now.return_value = touch_time
        returned_doc = doc.touch()

        # Verify we can chain methods
        assert returned_doc is doc
        assert isinstance(returned_doc, SampleModel)


# ── EncryptedFieldsMixin tests ────────────────────────────────────


class SecretModel(EncryptedFieldsMixin):
    """Test model with multiple encrypted and plain fields."""

    api_key: EncryptedStr = Field(default="test-key")
    optional_token: EncryptedStr | None = Field(default=None)
    plain_field: str = Field(default="not-encrypted")


class TestEncryptedFieldsMixin:
    """Tests for transparent encrypt-on-save / decrypt-on-load of EncryptedStr fields."""

    PASSPHRASE = "test-encryption-key"

    def test_field_discovery(self):
        """_encrypted_field_names returns only fields annotated with EncryptedStr."""
        names = _encrypted_field_names(SecretModel)
        assert names == {"api_key", "optional_token"}

    def test_encrypt_on_insert(self, monkeypatch):
        """before_event(Insert) encrypts plaintext fields when key is set."""
        monkeypatch.setattr(settings, "field_encryption_key", self.PASSPHRASE)
        model = SecretModel(api_key="my-key")
        model._encrypt_on_insert()

        from vibetuner.crypto import is_encrypted

        assert is_encrypted(model.api_key)

    def test_encrypt_on_update(self, monkeypatch):
        """before_event(Update/Save/...) encrypts plaintext fields."""
        monkeypatch.setattr(settings, "field_encryption_key", self.PASSPHRASE)
        model = SecretModel(api_key="my-key")
        model._encrypt_on_update()

        from vibetuner.crypto import is_encrypted

        assert is_encrypted(model.api_key)

    def test_decrypt_on_load(self, monkeypatch):
        """model_validator decrypts ciphertext on model instantiation."""
        from vibetuner.crypto import encrypt_value

        monkeypatch.setattr(settings, "field_encryption_key", self.PASSPHRASE)
        ciphertext = encrypt_value("my-key", self.PASSPHRASE)
        model = SecretModel(api_key=ciphertext)
        assert model.api_key == "my-key"

    def test_no_encryption_when_key_unset(self, monkeypatch):
        """Plaintext stays plaintext when no encryption key is configured."""
        monkeypatch.setattr(settings, "field_encryption_key", None)
        model = SecretModel(api_key="my-key")
        model._encrypt_on_insert()
        assert model.api_key == "my-key"

    def test_plaintext_passthrough_on_load(self, monkeypatch):
        """Plaintext values pass through the decrypt validator unchanged."""
        monkeypatch.setattr(settings, "field_encryption_key", self.PASSPHRASE)
        model = SecretModel(api_key="plain-key")
        assert model.api_key == "plain-key"

    def test_encrypted_without_key_raises_on_load(self, monkeypatch):
        """Loading an encrypted value with no key raises ValueError."""
        from vibetuner.crypto import encrypt_value

        monkeypatch.setattr(settings, "field_encryption_key", None)
        ciphertext = encrypt_value("my-key", self.PASSPHRASE)
        with pytest.raises(ValueError, match="encrypted.*no.*key"):
            SecretModel(api_key=ciphertext)

    def test_no_double_encryption(self, monkeypatch):
        """Calling encrypt hook on an already-encrypted value is idempotent."""
        from vibetuner.crypto import decrypt_value, encrypt_value

        monkeypatch.setattr(settings, "field_encryption_key", self.PASSPHRASE)
        ciphertext = encrypt_value("my-key", self.PASSPHRASE)
        model = SecretModel(api_key="placeholder")
        model.api_key = ciphertext
        model._encrypt_on_insert()
        assert decrypt_value(model.api_key, self.PASSPHRASE) == "my-key"

    def test_multiple_fields_encrypted(self, monkeypatch):
        """All EncryptedStr fields are encrypted, not just the first one."""
        monkeypatch.setattr(settings, "field_encryption_key", self.PASSPHRASE)
        model = SecretModel(api_key="key-1", optional_token="token-2")
        model._encrypt_on_insert()

        from vibetuner.crypto import is_encrypted

        assert is_encrypted(model.api_key)
        assert is_encrypted(model.optional_token)

    def test_optional_none_skipped(self, monkeypatch):
        """None values in optional EncryptedStr fields are left alone."""
        monkeypatch.setattr(settings, "field_encryption_key", self.PASSPHRASE)
        model = SecretModel(api_key="my-key", optional_token=None)
        model._encrypt_on_insert()

        from vibetuner.crypto import is_encrypted

        assert is_encrypted(model.api_key)
        assert model.optional_token is None

    def test_plain_field_untouched(self, monkeypatch):
        """Non-EncryptedStr fields are never encrypted."""
        monkeypatch.setattr(settings, "field_encryption_key", self.PASSPHRASE)
        model = SecretModel(api_key="my-key", plain_field="visible")
        model._encrypt_on_insert()
        assert model.plain_field == "visible"
