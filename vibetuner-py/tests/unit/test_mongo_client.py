# ABOUTME: Tests for the options the framework's MongoDB client is created with.
# ABOUTME: Ensures BSON datetimes decode as timezone-aware UTC values.
# ruff: noqa: S101
from collections.abc import Iterator

import pytest
import vibetuner.mongo as mongo_mod
from pydantic import MongoDsn
from vibetuner.config import settings


@pytest.fixture
def local_mongodb_url() -> Iterator[None]:
    """Point settings at a dummy URL; the client never connects in these tests."""
    original_url = settings.mongodb_url
    original_client = mongo_mod.mongo_client
    settings.mongodb_url = MongoDsn("mongodb://localhost:27017")
    mongo_mod.mongo_client = None
    try:
        yield
    finally:
        settings.mongodb_url = original_url
        mongo_mod.mongo_client = original_client


def test_global_client_decodes_datetimes_as_timezone_aware(
    local_mongodb_url: None,
) -> None:
    mongo_mod._ensure_client()

    assert mongo_mod.mongo_client is not None
    assert mongo_mod.mongo_client.codec_options.tz_aware is True
