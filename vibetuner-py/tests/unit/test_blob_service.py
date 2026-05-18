# ABOUTME: Unit tests for BlobService construction and object_exists method
# ABOUTME: Covers default-bucket resolution warnings and check_bucket existence checks
# ruff: noqa: S101

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import HttpUrl, SecretStr


@pytest.fixture
def mock_storage():
    """Fixture for a mocked S3StorageService."""
    return AsyncMock()


@pytest.fixture
def blob_service(mock_storage):
    """Fixture for BlobService with mocked storage, bypassing __init__."""
    from vibetuner.services.blob import BlobService

    # Create instance without calling __init__ to avoid settings validation
    service = object.__new__(BlobService)
    service.storage = mock_storage
    service.default_bucket = "test-bucket"
    return service


@pytest.mark.asyncio
async def test_object_exists_blob_not_found_in_mongo(blob_service):
    """Test object_exists when BlobModel.get returns None."""
    with patch(
        "vibetuner.services.blob.BlobModel.get", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = None

        exists = await blob_service.object_exists("nonexistent_key")

        assert not exists
        blob_service.storage.object_exists.assert_not_called()


@pytest.mark.asyncio
async def test_object_exists_blob_found_in_mongo_no_check_bucket(blob_service):
    """Test object_exists when BlobModel.get returns a blob and check_bucket is False."""
    mock_blob = MagicMock()
    mock_blob.full_path = "test/path"
    mock_blob.bucket = "test-bucket"

    with patch(
        "vibetuner.services.blob.BlobModel.get", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = mock_blob

        exists = await blob_service.object_exists("existing_key", check_bucket=False)

        assert exists
        blob_service.storage.object_exists.assert_not_called()


@pytest.mark.asyncio
async def test_object_exists_blob_found_in_mongo_and_s3(blob_service):
    """Test object_exists when BlobModel exists and S3 confirms existence."""
    mock_blob = MagicMock()
    mock_blob.full_path = "test/path"
    mock_blob.bucket = "test-bucket"

    with patch(
        "vibetuner.services.blob.BlobModel.get", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = mock_blob
        blob_service.storage.object_exists.return_value = True

        exists = await blob_service.object_exists("existing_key", check_bucket=True)

        assert exists
        blob_service.storage.object_exists.assert_called_once_with(
            key="test/path", bucket="test-bucket"
        )


@pytest.mark.asyncio
async def test_object_exists_blob_found_in_mongo_but_not_s3(blob_service):
    """Test object_exists when BlobModel exists but S3 does not confirm existence."""
    mock_blob = MagicMock()
    mock_blob.full_path = "test/path"
    mock_blob.bucket = "test-bucket"

    with patch(
        "vibetuner.services.blob.BlobModel.get", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = mock_blob
        blob_service.storage.object_exists.return_value = False

        exists = await blob_service.object_exists("existing_key", check_bucket=True)

        assert not exists
        blob_service.storage.object_exists.assert_called_once_with(
            key="test/path", bucket="test-bucket"
        )


@pytest.fixture
def configured_r2_settings():
    """Patch settings with valid R2 credentials and a default bucket name."""
    from vibetuner.services import blob as blob_module

    with patch.object(blob_module, "settings") as mock_settings:
        mock_settings.r2_bucket_endpoint_url = HttpUrl("https://example.r2.com")
        mock_settings.r2_access_key = SecretStr("access")
        mock_settings.r2_secret_key = SecretStr("secret")
        mock_settings.r2_default_region = "auto"
        mock_settings.r2_default_bucket_name = "settings-bucket"
        yield mock_settings


@pytest.fixture
def reset_fallback_warning():
    """Reset the module-level flag that gates the implicit-fallback warning."""
    from vibetuner.services import blob as blob_module

    blob_module._implicit_fallback_warned = False
    yield
    blob_module._implicit_fallback_warned = False


def test_init_warns_on_implicit_default_bucket_fallback(
    configured_r2_settings, reset_fallback_warning, log_sink
):
    """BlobService() without default_bucket logs a warning naming the fallback bucket."""
    from vibetuner.services.blob import BlobService

    with patch("vibetuner.services.blob.S3StorageService"):
        service = BlobService()

    assert service.default_bucket == "settings-bucket"
    assert any(
        "settings-bucket" in m and "R2_DEFAULT_BUCKET_NAME" in m for m in log_sink
    ), f"Expected fallback warning naming the bucket, got: {log_sink}"


def test_init_warning_logged_only_once_per_process(
    configured_r2_settings, reset_fallback_warning, log_sink
):
    """The implicit-fallback warning fires once per process, not per instance."""
    from vibetuner.services.blob import BlobService

    with patch("vibetuner.services.blob.S3StorageService"):
        BlobService()
        BlobService()
        BlobService()

    matches = [m for m in log_sink if "R2_DEFAULT_BUCKET_NAME" in m]
    assert len(matches) == 1, (
        f"Expected exactly one fallback warning, got {len(matches)}: {matches}"
    )


def test_init_no_warning_with_explicit_default_bucket(
    configured_r2_settings, reset_fallback_warning, log_sink
):
    """Passing default_bucket explicitly suppresses the fallback warning."""
    from vibetuner.services.blob import BlobService

    with patch("vibetuner.services.blob.S3StorageService"):
        service = BlobService(default_bucket="my-bucket")

    assert service.default_bucket == "my-bucket"
    assert not any("R2_DEFAULT_BUCKET_NAME" in m for m in log_sink), (
        f"Did not expect fallback warning, got: {log_sink}"
    )


def test_init_raises_when_no_bucket_configured(reset_fallback_warning):
    """No default_bucket arg and no settings.r2_default_bucket_name raises ValueError."""
    from vibetuner.services import blob as blob_module
    from vibetuner.services.blob import BlobService

    with patch.object(blob_module, "settings") as mock_settings:
        mock_settings.r2_bucket_endpoint_url = HttpUrl("https://example.r2.com")
        mock_settings.r2_access_key = SecretStr("access")
        mock_settings.r2_secret_key = SecretStr("secret")
        mock_settings.r2_default_region = "auto"
        mock_settings.r2_default_bucket_name = None

        with pytest.raises(ValueError, match="Default bucket name"):
            BlobService()
