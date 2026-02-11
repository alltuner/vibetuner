# ABOUTME: FastAPI dependency injection wrappers for built-in services.
# ABOUTME: Provides get_email_service, get_blob_service, get_runtime_config for use with Depends().

import asyncio
from collections.abc import AsyncGenerator

from fastapi import HTTPException

from vibetuner.logging import logger
from vibetuner.runtime_config import RuntimeConfig
from vibetuner.services.blob import BlobService
from vibetuner.services.email import EmailService, EmailServiceNotConfiguredError

_cache_lock = asyncio.Lock()


async def get_email_service() -> AsyncGenerator[EmailService, None]:
    """FastAPI dependency that provides an EmailService instance.

    Usage:
        @router.post("/send")
        async def send(email: EmailService = Depends(get_email_service)):
            await email.send_email(...)
    """
    try:
        service = EmailService()
    except EmailServiceNotConfiguredError as e:
        logger.error("Failed to initialize EmailService: {}", e)
        raise HTTPException(
            status_code=503, detail="Email service is not available"
        ) from e
    yield service


async def get_blob_service() -> AsyncGenerator[BlobService, None]:
    """FastAPI dependency that provides a BlobService instance.

    Usage:
        @router.post("/upload")
        async def upload(blobs: BlobService = Depends(get_blob_service)):
            await blobs.put_object(...)
    """
    try:
        service = BlobService()
    except ValueError as e:
        logger.error("Failed to initialize BlobService: {}", e)
        raise HTTPException(
            status_code=503, detail="Blob storage service is not available"
        ) from e
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
        async with _cache_lock:
            # Double-check after acquiring the lock
            if RuntimeConfig.is_cache_stale():
                await RuntimeConfig.refresh_cache()
    yield RuntimeConfig()
