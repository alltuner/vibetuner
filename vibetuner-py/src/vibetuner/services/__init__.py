# ABOUTME: FastAPI dependency injection wrappers for built-in services.
# ABOUTME: Provides get_email_service, get_blob_service, get_runtime_config for use with Depends().

from collections.abc import AsyncGenerator

from vibetuner.runtime_config import RuntimeConfig
from vibetuner.services.blob import BlobService
from vibetuner.services.email import EmailService


async def get_email_service() -> AsyncGenerator[EmailService, None]:
    """FastAPI dependency that provides an EmailService instance.

    Usage:
        @router.post("/send")
        async def send(email: EmailService = Depends(get_email_service)):
            await email.send_email(...)
    """
    service = EmailService()
    yield service


async def get_blob_service() -> AsyncGenerator[BlobService, None]:
    """FastAPI dependency that provides a BlobService instance.

    Usage:
        @router.post("/upload")
        async def upload(blobs: BlobService = Depends(get_blob_service)):
            await blobs.put_object(...)
    """
    service = BlobService()
    yield service


async def get_runtime_config() -> AsyncGenerator[RuntimeConfig, None]:
    """FastAPI dependency that provides a RuntimeConfig instance.

    Refreshes the config cache if stale before yielding.

    Usage:
        @router.get("/settings")
        async def settings(config: RuntimeConfig = Depends(get_runtime_config)):
            value = await config.get("features.dark_mode")
    """
    if RuntimeConfig.is_cache_stale():
        await RuntimeConfig.refresh_cache()
    yield RuntimeConfig()
