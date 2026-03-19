# ABOUTME: Tests for soft delete support.
# ABOUTME: Verifies re-export of DocumentWithSoftDelete and CRUD schema exclusion of deleted_at.
# ruff: noqa: S101

from beanie import DocumentWithSoftDelete
from vibetuner.crud import _build_create_schema, _build_update_schema
from vibetuner.models.mixins import TimeStampMixin


class SoftDeleteProduct(DocumentWithSoftDelete):
    """Test model using soft delete."""

    name: str
    price: float

    class Settings:
        name = "test_soft_delete_products"


class SoftDeleteWithTimestamps(DocumentWithSoftDelete, TimeStampMixin):
    """Test model combining soft delete with timestamps."""

    title: str

    class Settings:
        name = "test_soft_delete_timestamped"


class TestSoftDeleteReExport:
    """Test that DocumentWithSoftDelete is re-exported from vibetuner.models."""

    def test_importable_from_vibetuner_models(self):
        from vibetuner.models import DocumentWithSoftDelete as Cls

        assert Cls is DocumentWithSoftDelete

    def test_is_document_subclass(self):
        from beanie import Document

        assert issubclass(DocumentWithSoftDelete, Document)


class TestCrudSchemaExcludesDeletedAt:
    """Test that CRUD auto-generated schemas exclude deleted_at."""

    def test_create_schema_excludes_deleted_at(self):
        schema = _build_create_schema(SoftDeleteProduct)
        assert "deleted_at" not in schema.model_fields

    def test_create_schema_keeps_user_fields(self):
        schema = _build_create_schema(SoftDeleteProduct)
        assert "name" in schema.model_fields
        assert "price" in schema.model_fields

    def test_update_schema_excludes_deleted_at(self):
        create = _build_create_schema(SoftDeleteProduct)
        update = _build_update_schema(create)
        assert "deleted_at" not in update.model_fields

    def test_create_schema_excludes_deleted_at_with_timestamps(self):
        schema = _build_create_schema(SoftDeleteWithTimestamps)
        assert "deleted_at" not in schema.model_fields
        assert "db_insert_dt" not in schema.model_fields
        assert "db_update_dt" not in schema.model_fields
        assert "title" in schema.model_fields
