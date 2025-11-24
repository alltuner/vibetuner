"""Blob storage service for file uploads to S3 or R2.

WARNING: This is a scaffolding-managed file. DO NOT MODIFY directly.
To extend blob functionality, create wrapper services in the parent services directory.
"""

import mimetypes
from pathlib import Path

import aioboto3

from vibetuner.config import settings
from vibetuner.models import BlobModel
from vibetuner.models.blob import BlobStatus
from vibetuner.services.s3_storage import DEFAULT_CONTENT_TYPE, S3StorageService


class BlobService:
    def __init__(
        self,
        session: aioboto3.Session | None = None,
        default_bucket: str | None = None,
    ) -> None:
        if (
            settings.r2_bucket_endpoint_url is None
            or settings.r2_access_key is None
            or settings.r2_secret_key is None
        ):
            raise ValueError(
                "R2 bucket endpoint URL, access key, and secret key must be set in settings."
            )

        bucket = default_bucket or settings.r2_default_bucket_name
        if bucket is None:
            raise ValueError(
                "Default bucket name must be provided either in settings or as an argument."
            )

        self.storage = S3StorageService(
            endpoint_url=str(settings.r2_bucket_endpoint_url),
            access_key=settings.r2_access_key.get_secret_value(),
            secret_key=settings.r2_secret_key.get_secret_value(),
            region=settings.r2_default_region,
            default_bucket=bucket,
            session=session,
        )
        self.default_bucket = bucket

    async def put_object(
        self,
        body: bytes,
        content_type: str = DEFAULT_CONTENT_TYPE,
        bucket: str | None = None,
        namespace: str | None = None,
        original_filename: str | None = None,
    ) -> BlobModel:
        """Put an object into the R2 bucket and return the blob model"""

        bucket = bucket or self.default_bucket

        blob = BlobModel.from_bytes(
            body=body,
            content_type=content_type,
            bucket=bucket,
            namespace=namespace,
            original_filename=original_filename,
        )

        await blob.insert()

        if not blob.id:
            raise ValueError("Blob ID must be set before uploading to R2.")

        try:
            await self.storage.put_object(
                key=blob.full_path,
                body=body,
                content_type=content_type,
                bucket=bucket,
            )
            blob.status = BlobStatus.UPLOADED
        except Exception:
            blob.status = BlobStatus.ERROR
        finally:
            await blob.save()

        return blob

    async def put_object_with_extension(
        self,
        body: bytes,
        extension: str,
        bucket: str | None = None,
        namespace: str | None = None,
    ) -> BlobModel:
        """Put an object into the R2 bucket with content type guessed from extension"""
        content_type, _ = mimetypes.guess_type(f"file.{extension.lstrip('.')}")
        content_type = content_type or DEFAULT_CONTENT_TYPE

        return await self.put_object(body, content_type, bucket, namespace)

    async def put_file(
        self,
        file_path: Path | str,
        content_type: str | None = None,
        bucket: str | None = None,
        namespace: str | None = None,
    ) -> BlobModel:
        """Put a file from filesystem into the R2 bucket"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Auto-detect content type if not provided
        if content_type is None:
            content_type, _ = mimetypes.guess_type(str(file_path))
            content_type = content_type or DEFAULT_CONTENT_TYPE

        return await self.put_object(
            file_path.read_bytes(),
            content_type,
            bucket,
            namespace,
            original_filename=file_path.name,
        )

    async def get_object(self, key: str) -> bytes:
        """Retrieve an object from the R2 bucket"""
        blob = await BlobModel.get(key)
        if not blob:
            raise ValueError(f"Blob not found: {key}")

        return await self.storage.get_object(
            key=blob.full_path,
            bucket=blob.bucket,
        )

    async def delete_object(self, key: str) -> None:
        """Delete an object from the R2 bucket"""
        blob = await BlobModel.get(key)
        if not blob:
            raise ValueError(f"Blob not found: {key}")

        blob.status = BlobStatus.DELETED

        await blob.save()

    async def object_exists(self, key: str, check_bucket: bool = False) -> bool:
        """Check if an object exists in the R2 bucket"""

        blob = await BlobModel.get(key)
        if not blob:
            return False

        if check_bucket:
            return await self.storage.object_exists(
                key=blob.full_path, bucket=blob.bucket
            )

        return True
