"""Blob storage service for file uploads to S3 or R2.

WARNING: This is a scaffolding-managed file. DO NOT MODIFY directly.
To extend blob functionality, create wrapper services in the parent services directory.
"""

import mimetypes
from pathlib import Path
from typing import Literal

import aioboto3
from aiobotocore.config import AioConfig

from vibetuner.config import settings
from vibetuner.models import BlobModel
from vibetuner.models.blob import BlobStatus


S3_SERVICE_NAME: Literal["s3"] = "s3"
DEFAULT_CONTENT_TYPE: str = "application/octet-stream"


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
        self.session = session or aioboto3.Session(
            aws_access_key_id=settings.r2_access_key.get_secret_value(),
            aws_secret_access_key=settings.r2_secret_key.get_secret_value(),
            region_name=settings.r2_default_region,
        )
        self.endpoint_url = str(settings.r2_bucket_endpoint_url)
        self.config = AioConfig(
            request_checksum_calculation="when_required",
            response_checksum_validation="when_required",
        )

        if not default_bucket:
            if settings.r2_default_bucket_name is None:
                raise ValueError(
                    "Default bucket name must be provided either in settings or as an argument."
                )
            self.default_bucket = settings.r2_default_bucket_name
        else:
            self.default_bucket = default_bucket

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
            async with self.session.client(
                service_name=S3_SERVICE_NAME,
                endpoint_url=self.endpoint_url,
                config=self.config,
            ) as s3_client:
                await s3_client.put_object(
                    Bucket=bucket,
                    Key=blob.full_path,
                    Body=body,
                    ContentType=content_type,
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

        async with self.session.client(
            service_name=S3_SERVICE_NAME,
            endpoint_url=self.endpoint_url,
            config=self.config,
        ) as s3_client:
            response = await s3_client.get_object(
                Bucket=blob.bucket,
                Key=blob.full_path,
            )
            return await response["Body"].read()

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

        return True
