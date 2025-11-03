"""Blob storage model for file uploads and management.

WARNING: This is a scaffolding-managed file. DO NOT MODIFY directly.
Manages file metadata for S3 or local storage backends.
"""

import hashlib
from enum import StrEnum
from typing import Self

from beanie import Document
from pydantic import Field

from vibetuner.models.registry import register_model

from .mixins import TimeStampMixin


class BlobStatus(StrEnum):
    PENDING = "pending"
    UPLOADED = "uploaded"
    DELETED = "deleted"
    ERROR = "error"


@register_model
class BlobModel(Document, TimeStampMixin):
    status: BlobStatus = Field(
        default=BlobStatus.PENDING,
        description="Status of the blob indicating if it is pending, uploaded, or deleted",
    )
    bucket: str = Field(
        ...,
        description="Storage bucket name where the object is stored",
    )
    content_type: str = Field(
        ...,
        description="MIME type of the object (e.g., image/png, application/pdf)",
    )
    original_filename: str | None = Field(
        default=None,
        description="Original name of the file as uploaded by the user (if applicable)",
    )
    namespace: str | None = Field(
        default=None,
        description="Namespaces (prefixes) for the object, used for organization (optional)",
    )
    checksum: str = Field(
        ...,
        description="SHA256 hash of the object for integrity verification",
    )
    size: int = Field(..., description="Size of the object in bytes")

    @property
    def full_path(self) -> str:
        """Get the full path of the blob in the bucket."""
        if self.namespace:
            return f"{self.namespace}/{self.id}"
        else:
            return f"{self.id}"

    @classmethod
    def from_bytes(
        cls,
        body: bytes,
        content_type: str,
        bucket: str,
        namespace: str | None = None,
        original_filename: str | None = None,
    ) -> Self:
        """Create a BlobModel instance from raw bytes and metadata."""
        return cls(
            original_filename=original_filename,
            content_type=content_type,
            bucket=bucket,
            namespace=namespace,
            checksum=cls.calculate_checksum(body),
            size=len(body),
        )

    @staticmethod
    def calculate_checksum(body: bytes) -> str:
        """Calculate SHA256 checksum of the given bytes."""

        return hashlib.sha256(body).hexdigest()

    class Settings:
        name = "blobs"
        keep_nulls = False
