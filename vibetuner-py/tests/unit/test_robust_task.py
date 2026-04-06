# ABOUTME: Tests for the robust_task decorator and retry middleware.
# ABOUTME: Verifies TaskContext extraction from kwargs and retry/dead-letter behavior.
# ruff: noqa: S101

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import vibetuner.tasks.robust as robust_mod
from streaq import StreaqRetry
from streaq.types import TaskContext
from vibetuner.tasks.robust import (
    _configs,
    _ensure_middleware,
    _handle_permanent_failure,
    _RobustConfig,
)


@pytest.fixture(autouse=True)
def _reset_middleware_state():
    """Reset module-level middleware state between tests."""
    robust_mod._middleware_registered = False
    _configs.clear()
    yield
    robust_mod._middleware_registered = False
    _configs.clear()


def _make_task_context(
    fn_name: str = "my_task",
    task_id: str = "task-123",
    tries: int = 1,
    timeout: timedelta | int | None = None,
    ttl: timedelta | int | None = None,
) -> TaskContext:
    return TaskContext(
        fn_name=fn_name,
        task_id=task_id,
        timeout=timeout,
        tries=tries,
        ttl=ttl,
    )


class TestEnsureMiddleware:
    """Tests for _ensure_middleware registration and context extraction."""

    def test_rejects_none_worker(self):
        with pytest.raises(TypeError, match="valid Streaq worker"):
            _ensure_middleware(None)

    def test_rejects_worker_without_middleware_attr(self):
        with pytest.raises(TypeError, match="valid Streaq worker"):
            _ensure_middleware(object())

    def test_registers_middleware_once(self):
        worker = MagicMock()
        captured = []
        worker.middleware = lambda fn: captured.append(fn) or fn
        _ensure_middleware(worker)
        _ensure_middleware(worker)
        assert len(captured) == 1

    def test_resets_flag_on_registration_error(self):
        worker = MagicMock()
        worker.middleware = MagicMock(side_effect=RuntimeError("boom"))
        with pytest.raises(RuntimeError, match="boom"):
            _ensure_middleware(worker)
        assert not robust_mod._middleware_registered


class TestMiddlewareContextExtraction:
    """Verify middleware extracts TaskContext from kwargs (not ContextVar)."""

    def _register_and_get_wrapper(self):
        """Register middleware and return the inner wrapper function."""
        worker = MagicMock()
        captured = {}

        def fake_middleware_decorator(fn):
            captured["middleware_fn"] = fn
            return fn

        worker.middleware = fake_middleware_decorator
        _ensure_middleware(worker)
        return captured["middleware_fn"]

    @pytest.mark.asyncio
    async def test_passes_through_when_no_task_context_in_kwargs(self):
        middleware_fn = self._register_and_get_wrapper()
        next_fn = AsyncMock(return_value="result")
        wrapper = middleware_fn(next_fn)

        result = await wrapper("arg1", key="val")
        assert result == "result"
        next_fn.assert_awaited_once_with("arg1", key="val")

    @pytest.mark.asyncio
    async def test_passes_through_when_no_config_for_task(self):
        middleware_fn = self._register_and_get_wrapper()
        next_fn = AsyncMock(return_value="ok")
        ctx = _make_task_context(fn_name="unconfigured_task")
        wrapper = middleware_fn(next_fn)

        result = await wrapper("arg1", ctx=ctx)
        assert result == "ok"

    @pytest.mark.asyncio
    async def test_extracts_task_context_from_kwargs(self):
        """Core test: middleware finds TaskContext in kwargs by type."""
        middleware_fn = self._register_and_get_wrapper()
        _configs["my_task"] = _RobustConfig(
            max_retries=3, backoff_base=2.0, backoff_max=300.0, on_failure=None
        )
        next_fn = AsyncMock(return_value="success")
        ctx = _make_task_context(fn_name="my_task")
        wrapper = middleware_fn(next_fn)

        result = await wrapper(ctx=ctx)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_retries_on_failure_below_max(self):
        """Middleware raises StreaqRetry with backoff when tries < max_retries."""
        middleware_fn = self._register_and_get_wrapper()
        _configs["my_task"] = _RobustConfig(
            max_retries=3, backoff_base=2.0, backoff_max=300.0, on_failure=None
        )
        next_fn = AsyncMock(side_effect=ValueError("fail"))
        ctx = _make_task_context(fn_name="my_task", tries=1)
        wrapper = middleware_fn(next_fn)

        with pytest.raises(StreaqRetry):
            await wrapper(ctx=ctx)

    @pytest.mark.asyncio
    async def test_propagates_streaq_retry_without_wrapping(self):
        """StreaqRetry from the task itself should pass through unchanged."""
        middleware_fn = self._register_and_get_wrapper()
        _configs["my_task"] = _RobustConfig(
            max_retries=3, backoff_base=2.0, backoff_max=300.0, on_failure=None
        )
        original_retry = StreaqRetry(delay=42)
        next_fn = AsyncMock(side_effect=original_retry)
        ctx = _make_task_context(fn_name="my_task", tries=1)
        wrapper = middleware_fn(next_fn)

        with pytest.raises(StreaqRetry) as exc_info:
            await wrapper(ctx=ctx)
        assert exc_info.value is original_retry

    @pytest.mark.asyncio
    @patch("vibetuner.tasks.robust._handle_permanent_failure", new_callable=AsyncMock)
    async def test_permanent_failure_when_tries_exhausted(self, mock_handle):
        """When tries >= max_retries, handle permanent failure."""
        middleware_fn = self._register_and_get_wrapper()
        _configs["my_task"] = _RobustConfig(
            max_retries=3, backoff_base=2.0, backoff_max=300.0, on_failure=None
        )
        exc = ValueError("permanent")
        next_fn = AsyncMock(side_effect=exc)
        ctx = _make_task_context(fn_name="my_task", tries=3)
        wrapper = middleware_fn(next_fn)

        with pytest.raises(ValueError, match="permanent"):
            await wrapper(ctx=ctx)

        mock_handle.assert_awaited_once()
        call_args = mock_handle.call_args
        assert call_args[0][0] is ctx
        assert call_args[0][2] is exc

    @pytest.mark.asyncio
    async def test_context_found_regardless_of_kwarg_name(self):
        """TaskContext should be found by type, not by parameter name."""
        middleware_fn = self._register_and_get_wrapper()
        _configs["my_task"] = _RobustConfig(
            max_retries=3, backoff_base=2.0, backoff_max=300.0, on_failure=None
        )
        next_fn = AsyncMock(return_value="ok")
        ctx = _make_task_context(fn_name="my_task")
        wrapper = middleware_fn(next_fn)

        # Use a different kwarg name than "ctx"
        result = await wrapper(task_deps=ctx)
        assert result == "ok"


class TestHandlePermanentFailure:
    """Tests for _handle_permanent_failure dead letter recording."""

    @pytest.mark.asyncio
    @patch("vibetuner.tasks.robust.DeadLetterModel")
    async def test_saves_dead_letter(self, mock_model_cls):
        mock_instance = MagicMock()
        mock_instance.insert = AsyncMock()
        mock_model_cls.return_value = mock_instance

        ctx = _make_task_context(fn_name="broken_task", task_id="t-456", tries=5)
        config = _RobustConfig(
            max_retries=5, backoff_base=2.0, backoff_max=300.0, on_failure=None
        )
        exc = RuntimeError("kaboom")

        await _handle_permanent_failure(ctx, config, exc)

        mock_model_cls.assert_called_once()
        call_kwargs = mock_model_cls.call_args
        assert call_kwargs[1]["task_name"] == "broken_task"
        assert call_kwargs[1]["task_id"] == "t-456"
        assert call_kwargs[1]["tries"] == 5

    @pytest.mark.asyncio
    @patch("vibetuner.tasks.robust.DeadLetterModel")
    async def test_invokes_on_failure_callback(self, mock_model_cls):
        mock_instance = MagicMock()
        mock_instance.insert = AsyncMock()
        mock_model_cls.return_value = mock_instance

        callback = MagicMock()
        ctx = _make_task_context(fn_name="task1", task_id="t-1", tries=3)
        config = _RobustConfig(
            max_retries=3, backoff_base=2.0, backoff_max=300.0, on_failure=callback
        )
        exc = ValueError("boom")

        await _handle_permanent_failure(ctx, config, exc)

        callback.assert_called_once_with("task1", "t-1", exc)
