# ABOUTME: Tests for the run CLI module
# ABOUTME: Verifies worker process configuration and lifecycle behavior
# ruff: noqa: S101
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_streaq():
    """Provide mock streaq + watchfiles functions that return immediately."""
    mock_settings = MagicMock()
    mock_settings.workers_available = True
    mock_settings.debug = False

    with (
        patch("vibetuner.config.settings", mock_settings),
        patch("streaq.cli.run_worker") as mock_run_worker,
        patch("streaq.ui.run_web") as mock_run_web,
        patch("watchfiles.run_process") as mock_run_process,
    ):
        yield {
            "settings": mock_settings,
            "run_worker": mock_run_worker,
            "run_web": mock_run_web,
            "run_process": mock_run_process,
        }


class TestWorkerProcessDaemonFlag:
    """Worker child processes must be daemon so they don't orphan on unclean shutdown."""

    def test_worker_processes_are_daemon(self, mock_streaq):
        """All child processes spawned by _run_worker should have daemon=True."""
        created_processes: list[MagicMock] = []
        original_process = __import__("multiprocessing").Process

        class TrackingProcess(original_process):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                created_processes.append(self)

            def start(self):
                pass  # Don't actually start processes

            def terminate(self):
                pass  # Process was never started

            def join(self, timeout=None):
                pass  # Process was never started

        with patch("multiprocessing.Process", TrackingProcess):
            from vibetuner.cli.run import _run_worker

            _run_worker("dev", 9100, 1)

        # At minimum, the web UI process should be spawned
        assert len(created_processes) >= 1, "Expected at least one child process"
        for proc in created_processes:
            assert proc.daemon is True, (
                "Child process must be daemon to prevent orphans"
            )

    def test_multiple_worker_processes_are_daemon(self, mock_streaq):
        """With multiple workers, all spawned processes should be daemon."""
        created_processes: list = []
        original_process = __import__("multiprocessing").Process

        class TrackingProcess(original_process):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                created_processes.append(self)

            def start(self):
                pass

            def terminate(self):
                pass

            def join(self, timeout=None):
                pass

        with patch("multiprocessing.Process", TrackingProcess):
            from vibetuner.cli.run import _run_worker

            _run_worker("prod", 9100, 3)

        # 1 web UI + 2 extra workers = 3 processes
        assert len(created_processes) == 3
        for proc in created_processes:
            assert proc.daemon is True


class TestWorkerDevReloadPaths:
    """Dev worker must watch only the project's reload paths, not the entire cwd."""

    def test_dev_worker_uses_explicit_reload_paths(self, mock_streaq):
        """In dev mode, watchfiles.run_process must be called with paths.reload_paths."""
        fake_paths = [Path("/proj/src"), Path("/proj/templates/frontend")]

        with (
            patch("multiprocessing.Process") as mock_process,
            patch("vibetuner.cli.run.paths") as mock_paths,
        ):
            mock_paths.reload_paths = fake_paths
            mock_process.return_value = MagicMock()

            from vibetuner.cli.run import _run_worker

            _run_worker("dev", 9100, 1)

        mock_streaq["run_process"].assert_called_once()
        call_args = mock_streaq["run_process"].call_args
        assert list(call_args.args) == fake_paths
        # The target must be streaq's run_worker invoked with watch=False so we
        # don't double-wrap the worker in a second (cwd-wide) watchfiles process.
        assert call_args.kwargs["target"] is mock_streaq["run_worker"]
        target_args = call_args.kwargs["args"]
        assert target_args[2] is False, (
            "Inner streaq.run_worker must be called with watch=False"
        )

    def test_prod_worker_does_not_use_watchfiles(self, mock_streaq):
        """In prod mode, watchfiles.run_process must not be invoked."""
        with patch("multiprocessing.Process") as mock_process:
            mock_process.return_value = MagicMock()

            from vibetuner.cli.run import _run_worker

            _run_worker("prod", 9100, 1)

        mock_streaq["run_process"].assert_not_called()
        mock_streaq["run_worker"].assert_called_once()
        # streaq's watch flag must stay False in prod.
        assert mock_streaq["run_worker"].call_args.args[2] is False
