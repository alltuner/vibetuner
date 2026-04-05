# ABOUTME: Tests for vibetuner.cli.crypto CLI commands.
# ABOUTME: Verifies set-key and rotate-key error handling without requiring MongoDB.
# ruff: noqa: S101
from unittest.mock import AsyncMock, patch

from pydantic import Field
from typer.testing import CliRunner
from vibetuner.cli import app
from vibetuner.config import settings
from vibetuner.crypto import encrypt_value
from vibetuner.models.mixins import EncryptedFieldsMixin, EncryptedStr


runner = CliRunner()


class TestSetKeyEncryptedDataHandling:
    """set-key must handle pre-encrypted data gracefully (#1559, #1561)."""

    def test_set_key_with_pre_encrypted_data_shows_helpful_error(
        self, monkeypatch, tmp_path
    ):
        """When DB has data encrypted with an unknown key, print a clear error instead of crashing."""
        monkeypatch.setattr(settings, "field_encryption_key", None)

        ciphertext = encrypt_value("secret", "original-key")

        async def mock_to_list():
            """Simulate what Beanie does: model_validate triggers _decrypt_on_load."""

            class FakeDoc(EncryptedFieldsMixin):
                client_secret: EncryptedStr = Field(default="x")

            # This triggers _decrypt_on_load, which will raise because the
            # auto-generated key doesn't match the one used to encrypt
            FakeDoc(client_secret=ciphertext)

        env_file = tmp_path / ".env"

        with (
            patch("vibetuner.mongo.init_mongodb", new_callable=AsyncMock),
            patch(
                "vibetuner.models.oauth_app.OAuthProviderAppModel.find_all"
            ) as mock_find_all,
        ):
            mock_find_all.return_value.to_list = mock_to_list
            result = runner.invoke(
                app, ["crypto", "set-key", "--env-file", str(env_file)]
            )

        assert result.exit_code == 1
        assert "encrypted" in result.output.lower()

    def test_set_key_updates_in_memory_settings_before_loading(
        self, monkeypatch, tmp_path
    ):
        """set-key must set settings.field_encryption_key in memory before loading documents (#1561)."""
        monkeypatch.setattr(settings, "field_encryption_key", None)

        key_during_load = {}

        async def mock_to_list():
            key_during_load["value"] = settings.field_encryption_key
            return []

        env_file = tmp_path / ".env"

        with (
            patch("vibetuner.mongo.init_mongodb", new_callable=AsyncMock),
            patch(
                "vibetuner.models.oauth_app.OAuthProviderAppModel.find_all"
            ) as mock_find_all,
            patch("vibetuner.crypto.write_env_var"),
        ):
            mock_find_all.return_value.to_list = mock_to_list
            result = runner.invoke(
                app,
                [
                    "crypto",
                    "set-key",
                    "--key",
                    "my-test-key",
                    "--env-file",
                    str(env_file),
                ],
            )

        assert result.exit_code == 0
        assert key_during_load["value"] == "my-test-key"
