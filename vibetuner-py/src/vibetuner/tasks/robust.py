# ABOUTME: Robust task decorator with retries, dead letters, and failure notifications.
# ABOUTME: Wraps Streaq tasks with exponential backoff and MongoDB dead letter collection.

import asyncio
import threading
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Callable

from beanie import Document
from pydantic import Field

from vibetuner.logging import logger


class DeadLetterModel(Document):
    """Tasks that permanently failed after exhausting all retries."""

    task_name: str
    task_id: str
    error: str
    error_type: str
    tries: int
    failed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "dead_letters"
        indexes = ["task_name", "failed_at"]


@dataclass
class _RobustConfig:
    max_retries: int
    backoff_base: float
    backoff_max: float
    on_failure: Callable[..., Any] | None


_configs: dict[str, _RobustConfig] = {}
_middleware_lock = threading.Lock()
_middleware_registered = False


async def _handle_permanent_failure(
    ctx: Any, config: _RobustConfig, exc: Exception
) -> None:
    """Save dead letter and invoke failure callback after all retries exhausted."""
    logger.error(
        "Task %s[%s] failed permanently after %d tries: %s",
        ctx.fn_name,
        ctx.task_id,
        ctx.tries,
        exc,
    )
    try:
        await DeadLetterModel(
            task_name=ctx.fn_name,
            task_id=ctx.task_id,
            error=str(exc),
            error_type=type(exc).__qualname__,
            tries=ctx.tries,
        ).insert()
    except Exception:
        logger.exception("Failed to save dead letter for %s", ctx.fn_name)

    if config.on_failure is not None:
        try:
            result = config.on_failure(ctx.fn_name, ctx.task_id, exc)
            if asyncio.iscoroutine(result) or asyncio.isfuture(result):
                await result
        except Exception:
            logger.exception("on_failure callback raised for %s", ctx.fn_name)


def _ensure_middleware(worker: Any) -> None:
    """Register the robust task middleware once per worker."""
    global _middleware_registered
    with _middleware_lock:
        if _middleware_registered:
            return
        _middleware_registered = True

        from streaq import StreaqRetry

        @worker.middleware
        async def robust_retry_middleware(ctx: Any, next_handler: Any) -> Any:
            config = _configs.get(ctx.fn_name)
            if config is None:
                return await next_handler()

            try:
                return await next_handler()
            except StreaqRetry:
                raise
            except Exception as exc:
                if ctx.tries < config.max_retries:
                    delay = min(config.backoff_base**ctx.tries, config.backoff_max)
                    logger.warning(
                        "Task %s[%s] failed (try %d/%d), retrying in %.0fs: %s",
                        ctx.fn_name,
                        ctx.task_id,
                        ctx.tries,
                        config.max_retries,
                        delay,
                        exc,
                    )
                    raise StreaqRetry(delay=int(delay)) from exc

                await _handle_permanent_failure(ctx, config, exc)
                raise


def robust_task(
    *,
    max_retries: int = 3,
    backoff_base: float = 2.0,
    backoff_max: float = 300.0,
    timeout: timedelta | int | None = None,
    on_failure: Callable[..., Any] | None = None,
    **task_kwargs: Any,
) -> Callable:
    """Decorator that wraps a Streaq task with retry and failure handling.

    Failed tasks are stored in the ``dead_letters`` MongoDB collection after
    all retries are exhausted.  An optional *on_failure* callback is invoked
    on permanent failure and may be sync or async.

    Usage::

        from vibetuner.tasks.robust import robust_task

        @robust_task(max_retries=5, backoff_max=600)
        async def send_report(account_id: str, ctx=WorkerDepends()):
            ...

    Args:
        max_retries: Maximum number of attempts before giving up.
        backoff_base: Base for exponential backoff (delay = base ** tries).
        backoff_max: Maximum backoff delay in seconds.
        timeout: Task timeout (forwarded to ``worker.task()``).
        on_failure: Called on permanent failure with
            ``(task_name: str, task_id: str, exc: Exception)``.  May be async.
        **task_kwargs: Extra keyword arguments forwarded to ``worker.task()``.
    """
    from vibetuner.tasks.worker import get_worker

    worker = get_worker()
    _ensure_middleware(worker)

    def decorator(fn: Callable) -> Any:
        task_name = task_kwargs.get("name") or fn.__name__
        _configs[task_name] = _RobustConfig(
            max_retries=max_retries,
            backoff_base=backoff_base,
            backoff_max=backoff_max,
            on_failure=on_failure,
        )
        return worker.task(
            max_tries=max_retries,
            timeout=timeout,
            **task_kwargs,
        )(fn)

    return decorator
