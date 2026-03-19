# ABOUTME: Tests for OAuth app capability detection interface.
# ABOUTME: Covers the CapabilityDetector ABC, ScopeCapabilityDetector, and detect_capabilities().
# ruff: noqa: S101
import pytest
from vibetuner.frontend.oauth import (
    _PROVIDERS,
    PROVIDER_IDENTIFIERS,
    detect_capabilities,
)
from vibetuner.models.oauth import OauthProviderModel
from vibetuner.provider import CapabilityDetector, ScopeCapabilityDetector


@pytest.fixture(autouse=True)
def clean_provider_registry():
    """Clear provider registry before and after each test."""
    _PROVIDERS.clear()
    PROVIDER_IDENTIFIERS.clear()
    yield
    _PROVIDERS.clear()
    PROVIDER_IDENTIFIERS.clear()


class TestCapabilityDetectorABC:
    """Tests for the CapabilityDetector abstract base class."""

    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            CapabilityDetector()

    def test_subclass_must_implement_detect(self):
        class Incomplete(CapabilityDetector):
            pass

        with pytest.raises(TypeError):
            Incomplete()

    def test_subclass_with_detect_is_valid(self):
        class Valid(CapabilityDetector):
            async def detect(self, token):
                return []

        detector = Valid()
        assert isinstance(detector, CapabilityDetector)


class TestScopeCapabilityDetector:
    """Tests for the built-in scope-based capability detector."""

    @pytest.fixture()
    def detector(self):
        return ScopeCapabilityDetector()

    @pytest.mark.asyncio()
    async def test_extracts_space_separated_scopes(self, detector):
        token = {"scope": "openid email profile"}
        result = await detector.detect(token)
        assert result == ["openid", "email", "profile"]

    @pytest.mark.asyncio()
    async def test_empty_scope_string(self, detector):
        token = {"scope": ""}
        result = await detector.detect(token)
        assert result == []

    @pytest.mark.asyncio()
    async def test_missing_scope_key(self, detector):
        token = {"access_token": "abc123"}
        result = await detector.detect(token)
        assert result == []

    @pytest.mark.asyncio()
    async def test_scope_as_list(self, detector):
        token = {"scope": ["read", "write", "admin"]}
        result = await detector.detect(token)
        assert result == ["read", "write", "admin"]

    @pytest.mark.asyncio()
    async def test_single_scope(self, detector):
        token = {"scope": "user:email"}
        result = await detector.detect(token)
        assert result == ["user:email"]

    @pytest.mark.asyncio()
    async def test_strips_extra_whitespace(self, detector):
        token = {"scope": "  openid   email  "}
        result = await detector.detect(token)
        assert result == ["openid", "email"]


class TestOauthProviderModelDetector:
    """Tests for the capability_detector field on OauthProviderModel."""

    def test_defaults_to_none(self):
        provider = OauthProviderModel(
            identifier="id",
            scopes=["openid"],
        )
        assert provider.capability_detector is None

    def test_accepts_detector_instance(self):
        detector = ScopeCapabilityDetector()
        provider = OauthProviderModel(
            identifier="id",
            scopes=["openid"],
            capability_detector=detector,
        )
        assert provider.capability_detector is detector


class TestDetectCapabilities:
    """Tests for the detect_capabilities() utility function."""

    @pytest.mark.asyncio()
    async def test_returns_empty_for_unknown_provider(self):
        result = await detect_capabilities("nonexistent", {"scope": "openid"})
        assert result == []

    @pytest.mark.asyncio()
    async def test_returns_empty_when_no_detector(self):
        from vibetuner.frontend.oauth import register_oauth_provider

        provider = OauthProviderModel(
            identifier="id",
            scopes=["openid"],
            config={"TEST_CLIENT_ID": "id", "TEST_CLIENT_SECRET": "secret"},
        )
        register_oauth_provider("test_provider", provider)

        result = await detect_capabilities("test_provider", {"scope": "openid email"})
        assert result == []

    @pytest.mark.asyncio()
    async def test_delegates_to_provider_detector(self):
        from vibetuner.frontend.oauth import register_oauth_provider

        detector = ScopeCapabilityDetector()
        provider = OauthProviderModel(
            identifier="id",
            scopes=["openid"],
            config={"TEST_CLIENT_ID": "id", "TEST_CLIENT_SECRET": "secret"},
            capability_detector=detector,
        )
        register_oauth_provider("test_provider", provider)

        result = await detect_capabilities(
            "test_provider", {"scope": "openid email profile"}
        )
        assert result == ["openid", "email", "profile"]

    @pytest.mark.asyncio()
    async def test_custom_detector(self):
        from vibetuner.frontend.oauth import register_oauth_provider

        class FixedDetector(CapabilityDetector):
            async def detect(self, token):
                return ["post", "read"] if "access_token" in token else []

        provider = OauthProviderModel(
            identifier="id",
            scopes=["openid"],
            config={"TEST_CLIENT_ID": "id", "TEST_CLIENT_SECRET": "secret"},
            capability_detector=FixedDetector(),
        )
        register_oauth_provider("test_provider", provider)

        result = await detect_capabilities("test_provider", {"access_token": "abc123"})
        assert result == ["post", "read"]

        result_no_token = await detect_capabilities("test_provider", {})
        assert result_no_token == []
