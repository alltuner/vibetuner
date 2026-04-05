# ABOUTME: Tests for the database-backed OAuth app registry.
# ABOUTME: Covers model validation, Authlib client registration, and OAuth flow with app_id.
# ruff: noqa: S101, S105, S106
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import SecretStr, ValidationError
from vibetuner.config import settings
from vibetuner.frontend.oauth import (
    _PROVIDERS,
    PROVIDER_IDENTIFIERS,
    _authlib_name_for_app,
    _register_app_client,
    auto_register_providers,
    get_registered_providers,
    oauth,
    resolve_oauth_client,
)
from vibetuner.models.oauth_app import OAuthProviderAppModel


@pytest.fixture(autouse=True)
def mock_document_settings():
    """Allow OAuthProviderAppModel instantiation without MongoDB."""
    OAuthProviderAppModel._document_settings = MagicMock()
    yield
    OAuthProviderAppModel._document_settings = None


@pytest.fixture(autouse=True)
def clean_provider_registry():
    """Clear provider registry before and after each test."""
    _PROVIDERS.clear()
    PROVIDER_IDENTIFIERS.clear()
    yield
    _PROVIDERS.clear()
    PROVIDER_IDENTIFIERS.clear()


@pytest.fixture()
def registered_google(monkeypatch):
    """Register Google as a provider for tests that need it."""
    monkeypatch.setattr(settings, "google_client_id", SecretStr("env-google-id"))
    monkeypatch.setattr(
        settings, "google_client_secret", SecretStr("env-google-secret")
    )
    auto_register_providers(["google"])


class TestOAuthProviderAppModel:
    """Tests for model validation."""

    def test_required_fields(self):
        app = OAuthProviderAppModel(
            provider="google",
            name="My App",
            client_id="test-id",
            client_secret="test-secret",
        )
        assert app.provider == "google"
        assert app.name == "My App"
        assert app.client_id == "test-id"
        assert app.client_secret == "test-secret"

    def test_default_values(self):
        app = OAuthProviderAppModel(
            provider="google",
            name="My App",
            client_id="id",
            client_secret="secret",
        )
        assert app.external_app_id is None
        assert app.scopes == []
        assert app.capabilities == []
        assert app.is_active is True
        assert app.metadata == {}

    def test_all_fields(self):
        app = OAuthProviderAppModel(
            provider="linkedin",
            name="Corp App",
            client_id="id",
            client_secret="secret",
            external_app_id="ext-123",
            scopes=["r_liteprofile", "w_member_social"],
            capabilities=["post_as_org"],
            is_active=False,
            metadata={"org_id": "12345"},
        )
        assert app.external_app_id == "ext-123"
        assert app.scopes == ["r_liteprofile", "w_member_social"]
        assert app.capabilities == ["post_as_org"]
        assert app.is_active is False
        assert app.metadata == {"org_id": "12345"}

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            OAuthProviderAppModel(provider="google")

    def test_collection_name(self):
        assert OAuthProviderAppModel.Settings.name == "oauth_provider_apps"


class TestAuthLibClientNaming:
    """Tests for the deterministic client naming function."""

    def test_name_format(self):
        assert _authlib_name_for_app("google", "abc123") == "google__app_abc123"

    def test_different_providers(self):
        name_a = _authlib_name_for_app("google", "id1")
        name_b = _authlib_name_for_app("github", "id1")
        assert name_a != name_b

    def test_different_ids(self):
        name_a = _authlib_name_for_app("google", "id1")
        name_b = _authlib_name_for_app("google", "id2")
        assert name_a != name_b


class TestRegisterAppClient:
    """Tests for registering an Authlib client from a DB-backed app."""

    def test_registers_client_with_correct_name(self, registered_google):
        app = OAuthProviderAppModel(
            provider="google",
            name="Test App",
            client_id="app-client-id",
            client_secret="app-client-secret",
        )
        # Simulate having an ID
        from bson import ObjectId

        app.id = ObjectId()

        client_name = _register_app_client(app)
        expected_name = f"google__app_{app.id}"
        assert client_name == expected_name

        # Verify Authlib client can be created
        client = oauth.create_client(client_name)
        assert client is not None

    def test_uses_provider_endpoint_config(self, registered_google):
        """Provider params (endpoints) are passed through to the Authlib client."""
        app = OAuthProviderAppModel(
            provider="google",
            name="Test App",
            client_id="app-id",
            client_secret="app-secret",
        )
        from bson import ObjectId

        app.id = ObjectId()

        client_name = _register_app_client(app)

        # Client was registered and is usable (inherits provider's endpoints)
        client = oauth.create_client(client_name)
        assert client is not None

        # Verify it's distinct from the env-var client
        default_client = oauth.create_client("google")
        assert default_client is not None
        assert client is not default_client

    def test_overrides_scopes_when_specified(self, registered_google):
        app = OAuthProviderAppModel(
            provider="google",
            name="Custom Scopes",
            client_id="app-id",
            client_secret="app-secret",
            scopes=["custom_scope1", "custom_scope2"],
        )
        from bson import ObjectId

        app.id = ObjectId()

        client_name = _register_app_client(app)
        client = oauth.create_client(client_name)
        assert client.client_kwargs["scope"] == "custom_scope1 custom_scope2"

    def test_uses_provider_scopes_when_empty(self, registered_google):
        app = OAuthProviderAppModel(
            provider="google",
            name="Default Scopes",
            client_id="app-id",
            client_secret="app-secret",
            scopes=[],
        )
        from bson import ObjectId

        app.id = ObjectId()

        client_name = _register_app_client(app)
        client = oauth.create_client(client_name)
        assert client.client_kwargs["scope"] == "openid email profile"

    def test_passes_compliance_fix_through(self, registered_google, monkeypatch):
        """compliance_fix from the provider config is passed to oauth.register()."""
        from unittest.mock import patch

        from bson import ObjectId

        def my_fix(session, token):
            return token

        # Patch the provider config to include a compliance_fix
        from vibetuner.frontend.oauth import _PROVIDERS

        monkeypatch.setattr(_PROVIDERS["google"], "compliance_fix", my_fix)

        app = OAuthProviderAppModel(
            provider="google",
            name="With Fix",
            client_id="app-id",
            client_secret="app-secret",
        )
        app.id = ObjectId()

        with patch.object(oauth, "register") as mock_register:
            _register_app_client(app)
            mock_register.assert_called_once()
            assert mock_register.call_args.kwargs["compliance_fix"] is my_fix

    def test_omits_compliance_fix_when_none(self, registered_google):
        """compliance_fix=None should not be passed to oauth.register()."""
        from unittest.mock import patch

        from bson import ObjectId

        app = OAuthProviderAppModel(
            provider="google",
            name="No Fix",
            client_id="app-id",
            client_secret="app-secret",
        )
        app.id = ObjectId()

        with patch.object(oauth, "register") as mock_register:
            _register_app_client(app)
            mock_register.assert_called_once()
            assert "compliance_fix" not in mock_register.call_args.kwargs

    def test_raises_for_unknown_provider(self):
        app = OAuthProviderAppModel(
            provider="myspace",
            name="Test",
            client_id="id",
            client_secret="secret",
        )
        from bson import ObjectId

        app.id = ObjectId()

        with pytest.raises(ValueError, match="No registered provider 'myspace'"):
            _register_app_client(app)


class TestGetRegisteredProviders:
    """Tests for the get_registered_providers helper."""

    def test_empty_when_none_registered(self):
        assert get_registered_providers() == {}

    def test_returns_registered_providers(self, registered_google):
        providers = get_registered_providers()
        assert "google" in providers
        assert providers["google"].identifier == "sub"


class TestResolveOAuthClient:
    """Tests for resolving the Authlib client name from an optional app_id."""

    async def test_returns_provider_name_when_no_app_id(self):
        result = await resolve_oauth_client("google", None)
        assert result == "google"

    async def test_returns_app_client_name_for_valid_app(self, registered_google):
        from bson import ObjectId

        app_id = ObjectId()
        app = OAuthProviderAppModel(
            provider="google",
            name="Test App",
            client_id="app-id",
            client_secret="app-secret",
        )
        app.id = app_id

        with patch.object(
            OAuthProviderAppModel, "get", new_callable=AsyncMock, return_value=app
        ):
            result = await resolve_oauth_client("google", str(app_id))
            assert result == _authlib_name_for_app("google", str(app_id))

    async def test_raises_when_app_not_found(self, registered_google):
        with patch.object(
            OAuthProviderAppModel, "get", new_callable=AsyncMock, return_value=None
        ):
            with pytest.raises(ValueError, match="not found or inactive"):
                await resolve_oauth_client("google", "nonexistent-id")

    async def test_raises_when_app_inactive(self, registered_google):
        from bson import ObjectId

        app = OAuthProviderAppModel(
            provider="google",
            name="Inactive App",
            client_id="id",
            client_secret="secret",
            is_active=False,
        )
        app.id = ObjectId()

        with patch.object(
            OAuthProviderAppModel, "get", new_callable=AsyncMock, return_value=app
        ):
            with pytest.raises(ValueError, match="not found or inactive"):
                await resolve_oauth_client("google", str(app.id))

    async def test_raises_when_provider_mismatch(self, registered_google):
        from bson import ObjectId

        app = OAuthProviderAppModel(
            provider="github",
            name="Wrong Provider",
            client_id="id",
            client_secret="secret",
        )
        app.id = ObjectId()

        with patch.object(
            OAuthProviderAppModel, "get", new_callable=AsyncMock, return_value=app
        ):
            with pytest.raises(ValueError, match="provider 'github', not 'google'"):
                await resolve_oauth_client("google", str(app.id))


class TestOAuthAppEncryption:
    """Tests for transparent encrypt-on-save / decrypt-on-load of client_secret."""

    PASSPHRASE = "test-encryption-key"

    def test_encrypt_on_insert(self, monkeypatch):
        """before_event(Insert) encrypts plaintext client_secret when key is set."""
        monkeypatch.setattr(settings, "field_encryption_key", self.PASSPHRASE)
        app = OAuthProviderAppModel(
            provider="google",
            name="Test",
            client_id="id",
            client_secret="my-secret",
        )
        app.encrypt_on_insert()
        from vibetuner.crypto import is_encrypted

        assert is_encrypted(app.client_secret)

    def test_encrypt_on_update(self, monkeypatch):
        """before_event(Update/Save/...) encrypts plaintext client_secret."""
        monkeypatch.setattr(settings, "field_encryption_key", self.PASSPHRASE)
        app = OAuthProviderAppModel(
            provider="google",
            name="Test",
            client_id="id",
            client_secret="my-secret",
        )
        app.encrypt_on_update()
        from vibetuner.crypto import is_encrypted

        assert is_encrypted(app.client_secret)

    def test_decrypt_on_load(self, monkeypatch):
        """model_validator decrypts ciphertext on model instantiation."""
        from vibetuner.crypto import encrypt_value

        monkeypatch.setattr(settings, "field_encryption_key", self.PASSPHRASE)
        ciphertext = encrypt_value("my-secret", self.PASSPHRASE)
        app = OAuthProviderAppModel(
            provider="google",
            name="Test",
            client_id="id",
            client_secret=ciphertext,
        )
        assert app.client_secret == "my-secret"

    def test_no_encryption_when_key_unset(self, monkeypatch):
        """Plaintext stays plaintext when no encryption key is configured."""
        monkeypatch.setattr(settings, "field_encryption_key", None)
        app = OAuthProviderAppModel(
            provider="google",
            name="Test",
            client_id="id",
            client_secret="my-secret",
        )
        app.encrypt_on_insert()
        assert app.client_secret == "my-secret"

    def test_plaintext_passthrough_on_load(self, monkeypatch):
        """Plaintext values pass through the decrypt validator unchanged."""
        monkeypatch.setattr(settings, "field_encryption_key", self.PASSPHRASE)
        app = OAuthProviderAppModel(
            provider="google",
            name="Test",
            client_id="id",
            client_secret="plain-secret",
        )
        assert app.client_secret == "plain-secret"

    def test_encrypted_without_key_raises_on_load(self, monkeypatch):
        """Loading an encrypted value with no key raises ValueError."""
        from vibetuner.crypto import encrypt_value

        monkeypatch.setattr(settings, "field_encryption_key", None)
        ciphertext = encrypt_value("my-secret", self.PASSPHRASE)
        with pytest.raises(ValueError, match="encrypted.*no.*key"):
            OAuthProviderAppModel(
                provider="google",
                name="Test",
                client_id="id",
                client_secret=ciphertext,
            )

    def test_no_double_encryption(self, monkeypatch):
        """Calling encrypt hook on an already-encrypted value is idempotent."""
        from vibetuner.crypto import encrypt_value

        monkeypatch.setattr(settings, "field_encryption_key", self.PASSPHRASE)
        ciphertext = encrypt_value("my-secret", self.PASSPHRASE)
        app = OAuthProviderAppModel(
            provider="google",
            name="Test",
            client_id="id",
            # Bypass the decrypt validator by setting after construction
            client_secret="placeholder",
        )
        app.client_secret = ciphertext
        app.encrypt_on_insert()
        # Should still be the same ciphertext (not double-encrypted)
        from vibetuner.crypto import decrypt_value

        assert decrypt_value(app.client_secret, self.PASSPHRASE) == "my-secret"
