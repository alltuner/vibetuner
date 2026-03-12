# ABOUTME: Tests for the run CLI module
# ABOUTME: Verifies worker process configuration and lifecycle behavior
# ruff: noqa: S101
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_streaq():
    """Provide mock streaq functions that return immediately."""
    mock_settings = MagicMock()
    mock_settings.workers_available = True
    mock_settings.debug = False

    with (
        patch("vibetuner.config.settings", mock_settings),
        patch("streaq.cli.run_worker") as mock_run_worker,
        patch("streaq.ui.run_web") as mock_run_web,
    ):
        yield {
            "settings": mock_settings,
            "run_worker": mock_run_worker,
            "run_web": mock_run_web,
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
            assert proc.daemon is True, "Child process must be daemon to prevent orphans"

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
