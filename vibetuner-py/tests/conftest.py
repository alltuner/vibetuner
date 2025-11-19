# ABOUTME: Shared pytest fixtures and configuration for all tests
# ABOUTME: Provides common mocking utilities, time helpers, and temporary file fixtures

import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests with no external dependencies")
    config.addinivalue_line(
        "markers", "integration: Integration tests requiring external services"
    )
    config.addinivalue_line("markers", "slow: Tests that take longer to run")


def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests that need file system operations."""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


def mock_project_root(temp_dir: Path) -> Path:
    """Create a mock project root with common marker files."""
    # Create .copier-answers.yml to mark as project root
    copier_file = temp_dir / ".copier-answers.yml"
    copier_file.write_text("project_slug: test_project\nproject_name: Test Project\n")

    # Create typical directory structure
    (temp_dir / "templates").mkdir()
    (temp_dir / "src").mkdir()
    (temp_dir / "assets").mkdir()

    return temp_dir


def fixed_datetime() -> datetime:
    """Return a fixed datetime for testing time-dependent functions."""
    return datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)


def mock_datetime_now(monkeypatch, fixed_datetime: datetime):
    """Mock datetime.now() to return a fixed time."""

    def mock_now(tz=None):
        if tz is None:
            return fixed_datetime.replace(tzinfo=None)
        return fixed_datetime.replace(tzinfo=tz)

    monkeypatch.setattr("vibetuner.time.datetime", MagicMock(now=mock_now))
    return fixed_datetime


def sample_datetimes(fixed_datetime: datetime) -> dict[str, datetime]:
    """Provide sample datetimes at various intervals from fixed_datetime."""
    return {
        "now": fixed_datetime,
        "one_minute_ago": fixed_datetime - timedelta(minutes=1),
        "one_hour_ago": fixed_datetime - timedelta(hours=1),
        "one_day_ago": fixed_datetime - timedelta(days=1),
        "one_week_ago": fixed_datetime - timedelta(weeks=1),
        "thirty_days_ago": fixed_datetime - timedelta(days=30),
    }
