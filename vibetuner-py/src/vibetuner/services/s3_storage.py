"""ABOUTME: S3-compatible storage service for managing buckets and objects.
ABOUTME: Provides async operations for R2, MinIO, and other S3-compatible storage providers.
"""

from typing import Any, Literal

import aioboto3
from aiobotocore.config import AioConfig
from botocore.exceptions import ClientError


S3_SERVICE_NAME: Literal["s3"] = "s3"
DEFAULT_CONTENT_TYPE: str = "application/octet-stream"


class S3StorageService:
    """Async S3-compatible storage service for bucket and object operations.

    This service provides a clean interface to S3-compatible storage providers
    (AWS S3, Cloudflare R2, MinIO, etc.) without any database dependencies.

    All operations are async and use aioboto3 for efficient I/O.
    """

    def __init__(
        self,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        region: str = "auto",
        default_bucket: str | None = None,
        session: aioboto3.Session | None = None,
    ) -> None:
        """Initialize S3 storage service with explicit configuration.

        Args:
            endpoint_url: S3-compatible endpoint URL (e.g., "https://xxx.r2.cloudflarestorage.com")
            access_key: Access key ID for authentication
            secret_key: Secret access key for authentication
            region: AWS region (default "auto" for R2/MinIO)
            default_bucket: Optional default bucket for operations
            session: Optional custom aioboto3 session
        """
        self.endpoint_url = endpoint_url
        self.default_bucket = default_bucket
        self.session = session or aioboto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
        )
        self.config = AioConfig(
            request_checksum_calculation="when_required",
            response_checksum_validation="when_required",
        )

    def _get_bucket(self, bucket: str | None) -> str:
        """Get bucket name, using default if not specified.

        Args:
            bucket: Optional bucket name

        Returns:
            Bucket name to use

        Raises:
            ValueError: If no bucket specified and no default bucket set
        """
        if bucket is None:
            if self.default_bucket is None:
                raise ValueError(
                    "No bucket specified and no default bucket configured. "
                    "Provide bucket parameter or set default_bucket during initialization."
                )
            return self.default_bucket
        return bucket

    # =========================================================================
    # Object Operations
    # =========================================================================

    async def put_object(
        self,
        key: str,
        body: bytes,
        content_type: str = DEFAULT_CONTENT_TYPE,
        bucket: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> None:
        """Upload an object to S3-compatible storage.

        Args:
            key: Object key (path) in the bucket
            body: Raw bytes to upload
            content_type: MIME type of the object
            bucket: Bucket name (uses default_bucket if None)
            metadata: Optional custom metadata dict
        """
        bucket_name = self._get_bucket(bucket)

        async with self.session.client(
            service_name=S3_SERVICE_NAME,
            endpoint_url=self.endpoint_url,
            config=self.config,
        ) as s3_client:
            put_params: dict[str, Any] = {
                "Bucket": bucket_name,
                "Key": key,
                "Body": body,
                "ContentType": content_type,
            }
            if metadata:
                put_params["Metadata"] = metadata

            await s3_client.put_object(**put_params)

    async def get_object(self, key: str, bucket: str | None = None) -> bytes:
        """Retrieve an object from S3-compatible storage.

        Args:
            key: Object key (path) in the bucket
            bucket: Bucket name (uses default_bucket if None)

        Returns:
            Raw bytes of the object

        Raises:
            ClientError: If object doesn't exist or other S3 error
        """
        bucket_name = self._get_bucket(bucket)

        async with self.session.client(
            service_name=S3_SERVICE_NAME,
            endpoint_url=self.endpoint_url,
            config=self.config,
        ) as s3_client:
            response = await s3_client.get_object(
                Bucket=bucket_name,
                Key=key,
            )
            return await response["Body"].read()

    async def delete_object(self, key: str, bucket: str | None = None) -> None:
        """Delete an object from S3-compatible storage.

        Args:
            key: Object key (path) in the bucket
            bucket: Bucket name (uses default_bucket if None)
        """
        bucket_name = self._get_bucket(bucket)

        async with self.session.client(
            service_name=S3_SERVICE_NAME,
            endpoint_url=self.endpoint_url,
            config=self.config,
        ) as s3_client:
            await s3_client.delete_object(
                Bucket=bucket_name,
                Key=key,
            )

    async def object_exists(self, key: str, bucket: str | None = None) -> bool:
        """Check if an object exists in S3-compatible storage.

        Args:
            key: Object key (path) in the bucket
            bucket: Bucket name (uses default_bucket if None)

        Returns:
            True if object exists, False otherwise
        """
        bucket_name = self._get_bucket(bucket)

        try:
            async with self.session.client(
                service_name=S3_SERVICE_NAME,
                endpoint_url=self.endpoint_url,
                config=self.config,
            ) as s3_client:
                await s3_client.head_object(
                    Bucket=bucket_name,
                    Key=key,
                )
                return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "404":
                return False
            raise

    async def list_objects(
        self,
        prefix: str | None = None,
        bucket: str | None = None,
        max_keys: int = 1000,
    ) -> list[dict[str, Any]]:
        """List objects in a bucket with optional prefix filter.

        Args:
            prefix: Optional prefix to filter objects
            bucket: Bucket name (uses default_bucket if None)
            max_keys: Maximum number of keys to return (default 1000)

        Returns:
            List of object metadata dicts with keys: key, size, last_modified, etag
        """
        bucket_name = self._get_bucket(bucket)

        async with self.session.client(
            service_name=S3_SERVICE_NAME,
            endpoint_url=self.endpoint_url,
            config=self.config,
        ) as s3_client:
            list_params: dict[str, Any] = {
                "Bucket": bucket_name,
                "MaxKeys": max_keys,
            }
            if prefix:
                list_params["Prefix"] = prefix

            response = await s3_client.list_objects_v2(**list_params)

            if "Contents" not in response:
                return []

            return [
                {
                    "key": obj.get("Key", ""),
                    "size": obj.get("Size", 0),
                    "last_modified": obj.get("LastModified"),
                    "etag": obj.get("ETag", "").strip('"'),
                }
                for obj in response["Contents"]
            ]

    async def get_object_metadata(
        self, key: str, bucket: str | None = None
    ) -> dict[str, Any]:
        """Get metadata for an object without downloading it.

        Args:
            key: Object key (path) in the bucket
            bucket: Bucket name (uses default_bucket if None)

        Returns:
            Metadata dict with keys: content_type, size, last_modified, etag, metadata
        """
        bucket_name = self._get_bucket(bucket)

        async with self.session.client(
            service_name=S3_SERVICE_NAME,
            endpoint_url=self.endpoint_url,
            config=self.config,
        ) as s3_client:
            response = await s3_client.head_object(
                Bucket=bucket_name,
                Key=key,
            )

            return {
                "content_type": response.get("ContentType"),
                "size": response.get("ContentLength"),
                "last_modified": response.get("LastModified"),
                "etag": response.get("ETag", "").strip('"'),
                "metadata": response.get("Metadata", {}),
            }

    # =========================================================================
    # Bucket Operations
    # =========================================================================

    async def list_buckets(self) -> list[dict[str, Any]]:
        """List all buckets accessible with current credentials.

        Returns:
            List of bucket metadata dicts with keys: name, creation_date
        """
        async with self.session.client(
            service_name=S3_SERVICE_NAME,
            endpoint_url=self.endpoint_url,
            config=self.config,
        ) as s3_client:
            response = await s3_client.list_buckets()

            return [
                {
                    "name": bucket.get("Name", ""),
                    "creation_date": bucket.get("CreationDate"),
                }
                for bucket in response.get("Buckets", [])
            ]

    async def create_bucket(self, bucket: str, region: str | None = None) -> None:
        """Create a new bucket.

        Args:
            bucket: Name of the bucket to create
            region: Optional region (uses session default if None)
        """
        async with self.session.client(
            service_name=S3_SERVICE_NAME,
            endpoint_url=self.endpoint_url,
            config=self.config,
        ) as s3_client:
            create_params: dict[str, Any] = {"Bucket": bucket}

            # Only set CreateBucketConfiguration for non-us-east-1 regions
            if region and region not in ("us-east-1", "auto"):
                create_params["CreateBucketConfiguration"] = {
                    "LocationConstraint": region
                }

            await s3_client.create_bucket(**create_params)

    async def delete_bucket(self, bucket: str, force: bool = False) -> None:
        """Delete a bucket.

        Args:
            bucket: Name of the bucket to delete
            force: If True, delete all objects in bucket first

        Note:
            S3 buckets must be empty before deletion unless force=True
        """
        if force:
            # Delete all objects in the bucket first
            objects = await self.list_objects(bucket=bucket)
            async with self.session.client(
                service_name=S3_SERVICE_NAME,
                endpoint_url=self.endpoint_url,
                config=self.config,
            ) as s3_client:
                for obj in objects:
                    await s3_client.delete_object(
                        Bucket=bucket,
                        Key=obj["key"],
                    )

        async with self.session.client(
            service_name=S3_SERVICE_NAME,
            endpoint_url=self.endpoint_url,
            config=self.config,
        ) as s3_client:
            await s3_client.delete_bucket(Bucket=bucket)

    async def bucket_exists(self, bucket: str) -> bool:
        """Check if a bucket exists and is accessible.

        Args:
            bucket: Name of the bucket to check

        Returns:
            True if bucket exists and is accessible, False otherwise
        """
        try:
            async with self.session.client(
                service_name=S3_SERVICE_NAME,
                endpoint_url=self.endpoint_url,
                config=self.config,
            ) as s3_client:
                await s3_client.head_bucket(Bucket=bucket)
                return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code in ("404", "NoSuchBucket"):
                return False
            raise

    async def get_bucket_location(self, bucket: str) -> str:
        """Get the region/location of a bucket.

        Args:
            bucket: Name of the bucket

        Returns:
            Region string (e.g., "us-east-1", "auto")
        """
        async with self.session.client(
            service_name=S3_SERVICE_NAME,
            endpoint_url=self.endpoint_url,
            config=self.config,
        ) as s3_client:
            response = await s3_client.get_bucket_location(Bucket=bucket)
            location = response.get("LocationConstraint")
            # S3 returns None for us-east-1
            return location if location else "us-east-1"

    # =========================================================================
    # Advanced Operations
    # =========================================================================

    async def copy_object(
        self,
        src_key: str,
        dest_key: str,
        src_bucket: str | None = None,
        dest_bucket: str | None = None,
    ) -> None:
        """Copy an object from one location to another.

        Args:
            src_key: Source object key
            dest_key: Destination object key
            src_bucket: Source bucket (uses default_bucket if None)
            dest_bucket: Destination bucket (uses default_bucket if None)
        """
        src_bucket_name = self._get_bucket(src_bucket)
        dest_bucket_name = self._get_bucket(dest_bucket)

        async with self.session.client(
            service_name=S3_SERVICE_NAME,
            endpoint_url=self.endpoint_url,
            config=self.config,
        ) as s3_client:
            copy_source = f"{src_bucket_name}/{src_key}"
            await s3_client.copy_object(
                CopySource=copy_source,
                Bucket=dest_bucket_name,
                Key=dest_key,
            )

    async def generate_presigned_url(
        self,
        key: str,
        bucket: str | None = None,
        expiration: int = 3600,
        method: str = "get_object",
    ) -> str:
        """Generate a presigned URL for temporary access to an object.

        Args:
            key: Object key
            bucket: Bucket name (uses default_bucket if None)
            expiration: URL expiration time in seconds (default 3600 = 1 hour)
            method: S3 method name ("get_object" or "put_object")

        Returns:
            Presigned URL string
        """
        bucket_name = self._get_bucket(bucket)

        async with self.session.client(
            service_name=S3_SERVICE_NAME,
            endpoint_url=self.endpoint_url,
            config=self.config,
        ) as s3_client:
            url = await s3_client.generate_presigned_url(
                ClientMethod=method,
                Params={
                    "Bucket": bucket_name,
                    "Key": key,
                },
                ExpiresIn=expiration,
            )
            return url
