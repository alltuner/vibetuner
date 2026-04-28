import asyncio
import os
import time
from datetime import datetime
from typing import Any

from fastapi import APIRouter

from vibetuner.config import settings
from vibetuner.logging import logger
from vibetuner.paths import root as root_path


router = APIRouter(prefix="/health")

HEALTH_CHECK_TIMEOUT_SECONDS = 5


def _sanitize_error(e: Exception, *, service: str = "unknown") -> str:
    """Return a sanitized error message safe for health check responses.

    Strips connection strings, file paths, and other potentially sensitive
    information. Returns only the exception type for external consumers.
    """
    return f"{service}: service unavailable ({type(e).__name__})"


# Store startup time for instance identification and uptime calculation
_startup_time = datetime.now()
_startup_monotonic = time.monotonic()


@router.get("/ping")
def health_ping():
    """Liveness probe — always fast, no external calls."""
    return {"status": "ok"}


@router.get("")
async def health_check(detailed: bool = False):
    """Health check endpoint.

    Without query params, returns a fast liveness response.
    With ?detailed=true, checks all configured services and reports latency.
    """
    response: dict[str, Any] = {
        "status": "healthy",
        "version": settings.version,
        "uptime_seconds": round(time.monotonic() - _startup_monotonic),
    }

    if detailed:
        services = await _check_all_services()
        response["services"] = services
        # Mark unhealthy if any required service is down
        if any(s.get("status") == "error" for s in services.values()):
            response["status"] = "degraded"

    return response


@router.get("/ready")
async def health_ready():
    """Readiness probe — checks that all configured services are reachable."""
    services = await _check_all_services()
    all_ok = all(s.get("status") != "error" for s in services.values())

    return {
        "status": "ready" if all_ok else "not_ready",
        "services": services,
    }


@router.get("/id")
def health_instance_id():
    """Instance identification endpoint for distinguishing app instances."""
    if root_path is None:
        raise RuntimeError(
            "Project root not detected. Cannot provide instance information."
        )
    return {
        "app": settings.project.project_slug,
        "port": int(os.environ.get("PORT", 8000)),
        "debug": settings.debug,
        "status": "healthy",
        "root_path": str(root_path.resolve()),
        "process_id": os.getpid(),
        "startup_time": _startup_time.isoformat(),
    }


async def _check_all_services() -> dict[str, dict[str, Any]]:
    """Run health checks for all configured services."""
    from vibetuner.services.email.service import configured_provider

    services: dict[str, dict[str, Any]] = {}

    if settings.mongodb_url is not None:
        services["mongodb"] = await _check_mongodb()

    if settings.redis_url is not None:
        services["redis"] = await _check_redis()

    if settings.r2_bucket_endpoint_url is not None:
        services["s3"] = _check_s3()

    email_provider = configured_provider()
    if email_provider is not None:
        services["email"] = _check_email(email_provider)

    return services


async def _check_mongodb() -> dict[str, Any]:
    """Ping MongoDB and measure latency."""
    try:
        from vibetuner.mongo import mongo_client

        if mongo_client is None:
            return {"status": "not_initialized"}

        start = time.monotonic()
        async with asyncio.timeout(HEALTH_CHECK_TIMEOUT_SECONDS):
            await mongo_client.admin.command("ping")
        latency_ms = round((time.monotonic() - start) * 1000, 1)

        return {"status": "connected", "latency_ms": latency_ms}
    except TimeoutError:
        logger.warning("MongoDB health check timed out")
        return {"status": "error", "error": "Health check timed out"}
    except Exception as e:
        logger.warning("MongoDB health check failed: {}", e)
        return {"status": "error", "error": _sanitize_error(e, service="mongodb")}


async def _check_redis() -> dict[str, Any]:
    """Ping Redis and measure latency."""
    try:
        from vibetuner.redis import get_redis_client, reset_redis_client

        r = await get_redis_client()
        if r is None:
            return {"status": "not_initialized"}

        start = time.monotonic()
        async with asyncio.timeout(HEALTH_CHECK_TIMEOUT_SECONDS):
            await r.ping()
        latency_ms = round((time.monotonic() - start) * 1000, 1)
        return {"status": "connected", "latency_ms": latency_ms}
    except TimeoutError:
        logger.warning("Redis health check timed out")
        return {"status": "error", "error": "Health check timed out"}
    except Exception as e:
        logger.warning("Redis health check failed: {}", e)
        reset_redis_client()
        return {"status": "error", "error": _sanitize_error(e, service="redis")}


def _check_s3() -> dict[str, Any]:
    """Report S3/R2 configuration status (no live check to avoid latency)."""
    return {
        "status": "configured",
        "bucket": settings.r2_default_bucket_name,
    }


def _check_email(provider: str) -> dict[str, Any]:
    """Report email service configuration status."""
    return {
        "status": "configured",
        "provider": provider,
    }
