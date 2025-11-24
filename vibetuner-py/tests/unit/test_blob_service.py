# ABOUTME: Unit tests for BlobService.object_exists method
# ABOUTME: Tests check_bucket flag behavior for verifying blob existence in storage
# ruff: noqa: S101

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


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
