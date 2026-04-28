# ABOUTME: Integration test for vibetuner_db against a Dockerised MongoDB.
# ABOUTME: Verifies cross-test isolation, session DB reuse, and index persistence.
# ruff: noqa: S101
import os

import pytest
import vibetuner.mongo as mongo_mod
from beanie import Document
from pydantic import Field
from pymongo import IndexModel
from testcontainers.mongodb import MongoDbContainer
from vibetuner.config import settings
from vibetuner.mongo import get_all_models


class FixtureProbe(Document):
    """Test-only document used to exercise the vibetuner_db fixture."""

    label: str = Field(...)

    class Settings:
        name = "fixture_probe"
        indexes = [IndexModel("label", unique=True, name="fixture_probe_label_unique")]


_original_get_all_models = get_all_models


def _patched_get_all_models() -> list[type]:
    base = _original_get_all_models()
    if FixtureProbe not in base:
        base.append(FixtureProbe)
    return base


@pytest.fixture(scope="session", autouse=True)
def mongo_container():
    """Spin up a MongoDB container for the test session."""
    from pydantic import MongoDsn

    with MongoDbContainer("mongo:7") as container:
        url = container.get_connection_url()
        original_url = settings.mongodb_url
        settings.mongodb_url = MongoDsn(url)
        original_env = os.environ.get("MONGODB_URL")
        os.environ["MONGODB_URL"] = url
        # Patch model registry to include our probe.
        mongo_mod.get_all_models = _patched_get_all_models
        try:
            yield container
        finally:
            mongo_mod.get_all_models = _original_get_all_models
            settings.mongodb_url = original_url
            if original_env is None:
                os.environ.pop("MONGODB_URL", None)
            else:
                os.environ["MONGODB_URL"] = original_env


@pytest.mark.integration
class TestVibetunerDbIsolation:
    async def test_first_test_inserts_a_row(self, vibetuner_db):
        await FixtureProbe(label="from-test-1").insert()
        assert (
            await FixtureProbe.find_one(FixtureProbe.label == "from-test-1") is not None
        )

    async def test_second_test_sees_clean_state(self, vibetuner_db):
        # If the per-test cleanup works, the row from test 1 is gone.
        assert await FixtureProbe.find_one(FixtureProbe.label == "from-test-1") is None
        await FixtureProbe(label="from-test-2").insert()
        assert (
            await FixtureProbe.find_one(FixtureProbe.label == "from-test-2") is not None
        )

    async def test_uniqueness_index_still_enforced(self, vibetuner_db):
        # The unique index on ``label`` is built once at session scope and
        # persists across per-test cleanups, even though per-test
        # init_beanie runs with skip_indexes=True.
        from pymongo.errors import DuplicateKeyError

        await FixtureProbe(label="dup").insert()
        with pytest.raises(DuplicateKeyError):
            await FixtureProbe(label="dup").insert()
