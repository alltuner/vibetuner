# ABOUTME: Unit tests for vibetuner.time module
# ABOUTME: Tests time utility functions including now(), age calculations, and Unit enum
# ruff: noqa: S101

from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from vibetuner.time import Unit, age_in_days, age_in_minutes, age_in_timedelta, now


class TestUnit:
    """Test the Unit enum and its factor property."""

    def test_unit_values(self):
        """Test that Unit enum has correct string values."""
        assert Unit.SECONDS == "seconds"
        assert Unit.MINUTES == "minutes"
        assert Unit.HOURS == "hours"
        assert Unit.DAYS == "days"
        assert Unit.WEEKS == "weeks"

    def test_unit_factors(self):
        """Test that Unit.factor returns correct conversion factors."""
        assert Unit.SECONDS.factor == 1
        assert Unit.MINUTES.factor == 60
        assert Unit.HOURS.factor == 3_600
        assert Unit.DAYS.factor == 86_400
        assert Unit.WEEKS.factor == 604_800


class TestNow:
    """Test the now() function."""

    def test_now_returns_utc_datetime(self):
        """Test that now() returns a timezone-aware UTC datetime."""
        result = now()
        assert isinstance(result, datetime)
        assert result.tzinfo == UTC

    def test_now_returns_current_time(self):
        """Test that now() returns approximately the current time."""
        before = datetime.now(UTC)
        result = now()
        after = datetime.now(UTC)

        # Result should be between before and after (within a small window)
        assert before <= result <= after

    @patch("vibetuner.time.datetime")
    def test_now_uses_datetime_now(self, mock_datetime):
        """Test that now() calls datetime.now(UTC)."""
        fixed_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_datetime.now.return_value = fixed_time

        result = now()

        mock_datetime.now.assert_called_once_with(UTC)
        assert result == fixed_time


class TestAgeInDays:
    """Test the age_in_days() function."""

    @patch("vibetuner.time.now")
    def test_age_in_days_with_recent_datetime(self, mock_now):
        """Test calculating age in days for a datetime 3 days ago."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        three_days_ago = current_time - timedelta(days=3)
        result = age_in_days(three_days_ago)

        assert result == 3

    @patch("vibetuner.time.now")
    def test_age_in_days_with_hours(self, mock_now):
        """Test that partial days are truncated (not rounded)."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        # 1 day and 12 hours ago should return 1, not 2
        one_and_half_days_ago = current_time - timedelta(days=1, hours=12)
        result = age_in_days(one_and_half_days_ago)

        assert result == 1

    @patch("vibetuner.time.now")
    def test_age_in_days_with_naive_datetime(self, mock_now):
        """Test that naive datetimes are treated as UTC."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        # Pass a naive datetime (no timezone)
        five_days_ago_naive = datetime(2025, 1, 10, 12, 0, 0)
        result = age_in_days(five_days_ago_naive)

        assert result == 5

    @patch("vibetuner.time.now")
    def test_age_in_days_zero(self, mock_now):
        """Test that age_in_days returns 0 for current time."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        result = age_in_days(current_time)

        assert result == 0

    @patch("vibetuner.time.now")
    def test_age_in_days_large_value(self, mock_now):
        """Test age_in_days with a date far in the past."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        one_year_ago = current_time - timedelta(days=365)
        result = age_in_days(one_year_ago)

        assert result == 365


class TestAgeInMinutes:
    """Test the age_in_minutes() function."""

    @patch("vibetuner.time.now")
    def test_age_in_minutes_basic(self, mock_now):
        """Test calculating age in minutes for a datetime 30 minutes ago."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        thirty_minutes_ago = current_time - timedelta(minutes=30)
        result = age_in_minutes(thirty_minutes_ago)

        assert result == 30

    @patch("vibetuner.time.now")
    def test_age_in_minutes_with_seconds(self, mock_now):
        """Test that partial minutes are truncated (not rounded)."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        # 5 minutes and 45 seconds ago should return 5, not 6
        five_minutes_45_seconds_ago = current_time - timedelta(minutes=5, seconds=45)
        result = age_in_minutes(five_minutes_45_seconds_ago)

        assert result == 5

    @patch("vibetuner.time.now")
    def test_age_in_minutes_with_naive_datetime(self, mock_now):
        """Test that naive datetimes are treated as UTC."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        # Pass a naive datetime (no timezone)
        ten_minutes_ago_naive = datetime(2025, 1, 15, 11, 50, 0)
        result = age_in_minutes(ten_minutes_ago_naive)

        assert result == 10

    @patch("vibetuner.time.now")
    def test_age_in_minutes_zero(self, mock_now):
        """Test that age_in_minutes returns 0 for current time."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        result = age_in_minutes(current_time)

        assert result == 0

    @patch("vibetuner.time.now")
    def test_age_in_minutes_hours(self, mock_now):
        """Test age_in_minutes with hours."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        two_hours_ago = current_time - timedelta(hours=2)
        result = age_in_minutes(two_hours_ago)

        assert result == 120


class TestAgeInTimedelta:
    """Test the age_in_timedelta() function."""

    @patch("vibetuner.time.now")
    def test_age_in_timedelta_basic(self, mock_now):
        """Test that age_in_timedelta returns correct timedelta."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        three_hours_ago = current_time - timedelta(hours=3)
        result = age_in_timedelta(three_hours_ago)

        assert isinstance(result, timedelta)
        assert result == timedelta(hours=3)

    @patch("vibetuner.time.now")
    def test_age_in_timedelta_with_naive_datetime(self, mock_now):
        """Test that naive datetimes are treated as UTC."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        # Pass a naive datetime
        two_days_ago_naive = datetime(2025, 1, 13, 12, 0, 0)
        result = age_in_timedelta(two_days_ago_naive)

        assert result == timedelta(days=2)

    @patch("vibetuner.time.now")
    def test_age_in_timedelta_zero(self, mock_now):
        """Test that age_in_timedelta returns zero timedelta for current time."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        result = age_in_timedelta(current_time)

        assert result == timedelta(0)

    @patch("vibetuner.time.now")
    def test_age_in_timedelta_precision(self, mock_now):
        """Test that age_in_timedelta preserves microsecond precision."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, 123456, tzinfo=UTC)
        mock_now.return_value = current_time

        past_time = datetime(2025, 1, 15, 12, 0, 0, 23456, tzinfo=UTC)
        result = age_in_timedelta(past_time)

        assert result == timedelta(microseconds=100000)
