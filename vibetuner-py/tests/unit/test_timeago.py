# ABOUTME: Unit tests for the timeago, format_date, and format_datetime template filters
# ABOUTME: Tests both verbose (default) and short format output for relative time display
# ruff: noqa: S101

from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest
from vibetuner.frontend.templates import format_date, format_datetime, timeago


class TestTimeagoVerbose:
    """Test the default verbose timeago format."""

    @patch("vibetuner.time.now")
    def test_seconds_ago(self, mock_now):
        """Test that seconds are displayed correctly."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time - timedelta(seconds=30)
        result = timeago(dt)

        assert "30" in result
        assert "second" in result

    @patch("vibetuner.time.now")
    def test_minutes_ago(self, mock_now):
        """Test that minutes are displayed correctly."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time - timedelta(minutes=5)
        result = timeago(dt)

        assert "5" in result
        assert "minute" in result

    @patch("vibetuner.time.now")
    def test_hours_ago(self, mock_now):
        """Test that hours are displayed correctly."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time - timedelta(hours=3)
        result = timeago(dt)

        assert "3" in result
        assert "hour" in result

    @patch("vibetuner.time.now")
    def test_yesterday(self, mock_now):
        """Test that yesterday is displayed correctly."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time - timedelta(days=1, hours=12)
        result = timeago(dt)

        assert "yesterday" in result.lower()

    @patch("vibetuner.time.now")
    def test_days_ago(self, mock_now):
        """Test that days are displayed correctly."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time - timedelta(days=5)
        result = timeago(dt)

        assert "5" in result
        assert "day" in result

    @patch("vibetuner.time.now")
    def test_months_ago(self, mock_now):
        """Test that months are displayed correctly."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time - timedelta(days=90)
        result = timeago(dt)

        assert "3" in result
        assert "month" in result

    @patch("vibetuner.time.now")
    def test_years_ago(self, mock_now):
        """Test that years are displayed correctly."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time - timedelta(days=730)
        result = timeago(dt)

        assert "2" in result
        assert "year" in result

    @patch("vibetuner.time.now")
    def test_old_date_shows_formatted_date(self, mock_now):
        """Test that very old dates show formatted date."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = datetime(2020, 3, 15, tzinfo=UTC)
        result = timeago(dt)

        assert "Mar" in result
        assert "15" in result
        assert "2020" in result

    def test_invalid_input_returns_empty_string(self):
        """Test that invalid input returns empty string."""
        assert timeago(None) == ""
        assert timeago("not a date") == ""


class TestTimeagoShort:
    """Test the short timeago format."""

    @patch("vibetuner.time.now")
    def test_seconds_shows_just_now(self, mock_now):
        """Test that seconds show 'just now' in short format."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time - timedelta(seconds=30)
        result = timeago(dt, short=True)

        assert result == "just now"

    @patch("vibetuner.time.now")
    def test_one_minute_ago(self, mock_now):
        """Test that 1 minute shows '1m ago'."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time - timedelta(minutes=1)
        result = timeago(dt, short=True)

        assert result == "1m ago"

    @patch("vibetuner.time.now")
    def test_minutes_ago(self, mock_now):
        """Test that minutes show 'Xm ago' in short format."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time - timedelta(minutes=45)
        result = timeago(dt, short=True)

        assert result == "45m ago"

    @patch("vibetuner.time.now")
    def test_one_hour_ago(self, mock_now):
        """Test that 1 hour shows '1h ago'."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time - timedelta(hours=1)
        result = timeago(dt, short=True)

        assert result == "1h ago"

    @patch("vibetuner.time.now")
    def test_hours_ago(self, mock_now):
        """Test that hours show 'Xh ago' in short format."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time - timedelta(hours=8)
        result = timeago(dt, short=True)

        assert result == "8h ago"

    @patch("vibetuner.time.now")
    def test_yesterday_shows_1d_ago(self, mock_now):
        """Test that yesterday shows '1d ago' in short format."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time - timedelta(days=1, hours=12)
        result = timeago(dt, short=True)

        assert result == "1d ago"

    @patch("vibetuner.time.now")
    def test_days_ago(self, mock_now):
        """Test that days (2-6) show 'Xd ago' in short format."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time - timedelta(days=5)
        result = timeago(dt, short=True)

        assert result == "5d ago"

    @patch("vibetuner.time.now")
    def test_one_week_ago(self, mock_now):
        """Test that 7 days shows '1w ago' in short format."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time - timedelta(days=7)
        result = timeago(dt, short=True)

        assert result == "1w ago"

    @patch("vibetuner.time.now")
    def test_two_weeks_ago(self, mock_now):
        """Test that 14 days shows '2w ago' in short format."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time - timedelta(days=14)
        result = timeago(dt, short=True)

        assert result == "2w ago"

    @patch("vibetuner.time.now")
    def test_three_weeks_ago(self, mock_now):
        """Test that 21 days shows '3w ago' in short format."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time - timedelta(days=21)
        result = timeago(dt, short=True)

        assert result == "3w ago"

    @patch("vibetuner.time.now")
    def test_four_weeks_ago(self, mock_now):
        """Test that 28 days shows '4w ago' in short format."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time - timedelta(days=28)
        result = timeago(dt, short=True)

        assert result == "4w ago"

    @patch("vibetuner.time.now")
    def test_one_month_ago(self, mock_now):
        """Test that ~30 days shows '1mo ago' in short format."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time - timedelta(days=35)
        result = timeago(dt, short=True)

        assert result == "1mo ago"

    @patch("vibetuner.time.now")
    def test_months_ago(self, mock_now):
        """Test that months show 'Xmo ago' in short format."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time - timedelta(days=90)
        result = timeago(dt, short=True)

        assert result == "3mo ago"

    @patch("vibetuner.time.now")
    def test_one_year_ago(self, mock_now):
        """Test that ~365 days shows '1y ago' in short format."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time - timedelta(days=400)
        result = timeago(dt, short=True)

        assert result == "1y ago"

    @patch("vibetuner.time.now")
    def test_years_ago(self, mock_now):
        """Test that years show 'Xy ago' in short format."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time - timedelta(days=730)
        result = timeago(dt, short=True)

        assert result == "2y ago"

    @patch("vibetuner.time.now")
    def test_old_date_shows_formatted_date(self, mock_now):
        """Test that very old dates show formatted date in short format too."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = datetime(2020, 3, 15, tzinfo=UTC)
        result = timeago(dt, short=True)

        assert "Mar" in result
        assert "15" in result
        assert "2020" in result

    def test_invalid_input_returns_empty_string(self):
        """Test that invalid input returns empty string in short format."""
        assert timeago(None, short=True) == ""
        assert timeago("not a date", short=True) == ""


class TestTimeagoFutureVerbose:
    """Test the verbose timeago format for future datetimes."""

    @patch("vibetuner.time.now")
    def test_in_seconds(self, mock_now):
        """Test that future seconds are displayed correctly."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time + timedelta(seconds=30)
        result = timeago(dt)

        assert result == "in 30 seconds"

    @patch("vibetuner.time.now")
    def test_in_one_second(self, mock_now):
        """Test that one future second uses the singular form."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time + timedelta(seconds=1)
        result = timeago(dt)

        assert result == "in 1 second"

    @patch("vibetuner.time.now")
    def test_in_minutes(self, mock_now):
        """Test that future minutes are displayed correctly."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time + timedelta(minutes=5)
        result = timeago(dt)

        assert result == "in 5 minutes"

    @patch("vibetuner.time.now")
    def test_in_hours(self, mock_now):
        """Test that future hours are displayed correctly."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time + timedelta(hours=23, minutes=39)
        result = timeago(dt)

        assert result == "in 23 hours"

    @patch("vibetuner.time.now")
    def test_tomorrow(self, mock_now):
        """Test that a datetime one to two days away shows tomorrow."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time + timedelta(days=1, hours=12)
        result = timeago(dt)

        assert "tomorrow" in result.lower()

    @patch("vibetuner.time.now")
    def test_in_days(self, mock_now):
        """Test that future days are displayed correctly."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time + timedelta(days=5)
        result = timeago(dt)

        assert result == "in 5 days"

    @patch("vibetuner.time.now")
    def test_in_months(self, mock_now):
        """Test that future months are displayed correctly."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time + timedelta(days=90)
        result = timeago(dt)

        assert result == "in 3 months"

    @patch("vibetuner.time.now")
    def test_in_years(self, mock_now):
        """Test that future years are displayed correctly."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time + timedelta(days=730)
        result = timeago(dt)

        assert result == "in 2 years"

    @patch("vibetuner.time.now")
    def test_far_future_date_shows_formatted_date(self, mock_now):
        """Test that dates more than 4 years away show formatted date."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = datetime(2030, 3, 15, tzinfo=UTC)
        result = timeago(dt)

        assert "Mar" in result
        assert "15" in result
        assert "2030" in result


class TestTimeagoFutureShort:
    """Test the short timeago format for future datetimes."""

    @patch("vibetuner.time.now")
    def test_seconds_shows_just_now(self, mock_now):
        """Test that future seconds show 'just now' in short format."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time + timedelta(seconds=30)
        result = timeago(dt, short=True)

        assert result == "just now"

    @patch("vibetuner.time.now")
    def test_in_minutes(self, mock_now):
        """Test that future minutes show 'in Xm' in short format."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time + timedelta(minutes=45)
        result = timeago(dt, short=True)

        assert result == "in 45m"

    @patch("vibetuner.time.now")
    def test_in_hours(self, mock_now):
        """Test that future hours show 'in Xh' in short format."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time + timedelta(hours=23, minutes=39)
        result = timeago(dt, short=True)

        assert result == "in 23h"

    @patch("vibetuner.time.now")
    def test_tomorrow_shows_in_1d(self, mock_now):
        """Test that tomorrow shows 'in 1d' in short format."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time + timedelta(days=1, hours=12)
        result = timeago(dt, short=True)

        assert result == "in 1d"

    @patch("vibetuner.time.now")
    def test_in_days(self, mock_now):
        """Test that future days (2-6) show 'in Xd' in short format."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time + timedelta(days=5)
        result = timeago(dt, short=True)

        assert result == "in 5d"

    @patch("vibetuner.time.now")
    def test_in_weeks(self, mock_now):
        """Test that future weeks show 'in Xw' in short format."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time + timedelta(days=14)
        result = timeago(dt, short=True)

        assert result == "in 2w"

    @patch("vibetuner.time.now")
    def test_in_months(self, mock_now):
        """Test that future months show 'in Xmo' in short format."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time + timedelta(days=90)
        result = timeago(dt, short=True)

        assert result == "in 3mo"

    @patch("vibetuner.time.now")
    def test_in_years(self, mock_now):
        """Test that future years show 'in Xy' in short format."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time + timedelta(days=730)
        result = timeago(dt, short=True)

        assert result == "in 2y"

    @patch("vibetuner.time.now")
    def test_far_future_date_shows_formatted_date(self, mock_now):
        """Test that dates more than 4 years away show formatted date."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = datetime(2030, 3, 15, tzinfo=UTC)
        result = timeago(dt, short=True)

        assert "Mar" in result
        assert "15" in result
        assert "2030" in result


class TestTimeagoEdgeCases:
    """Test edge cases and threshold boundaries."""

    @patch("vibetuner.time.now")
    def test_exactly_60_seconds_shows_minutes(self, mock_now):
        """Test that exactly 60 seconds shows minutes, not seconds."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time - timedelta(seconds=60)
        result = timeago(dt)

        assert "minute" in result
        assert "second" not in result

    @patch("vibetuner.time.now")
    def test_exactly_60_minutes_shows_hours(self, mock_now):
        """Test that exactly 60 minutes shows hours, not minutes."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time - timedelta(minutes=60)
        result = timeago(dt)

        assert "hour" in result
        assert "minute" not in result

    @patch("vibetuner.time.now")
    def test_exactly_24_hours_shows_yesterday(self, mock_now):
        """Test that exactly 24 hours shows yesterday."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time - timedelta(hours=24)
        result = timeago(dt)

        assert "yesterday" in result.lower()

    @patch("vibetuner.time.now")
    def test_short_format_at_7_days_boundary(self, mock_now):
        """Test that 7 days shows weeks in short format."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time - timedelta(days=7)
        result = timeago(dt, short=True)

        assert result == "1w ago"

    @patch("vibetuner.time.now")
    def test_short_format_at_30_days_boundary(self, mock_now):
        """Test that 30 days shows months in short format."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time - timedelta(days=30)
        result = timeago(dt, short=True)

        assert result == "1mo ago"

    @patch("vibetuner.time.now")
    def test_verbose_format_at_7_days_shows_days(self, mock_now):
        """Test that 7 days in verbose format still shows days, not weeks."""
        current_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = current_time

        dt = current_time - timedelta(days=7)
        result = timeago(dt)

        assert "7" in result
        assert "day" in result
        assert "week" not in result.lower()


class TestFilterErrorHandling:
    """Test that date/time filters log warnings on invalid input and let unexpected exceptions propagate."""

    def test_timeago_bad_input_logs_warning_and_returns_empty(self, log_sink):
        """timeago() logs a WARNING when given a non-datetime value."""
        result = timeago("not a date")
        assert result == ""
        assert any("WARNING" in m for m in log_sink)

    def test_timeago_none_logs_warning_and_returns_empty(self, log_sink):
        """timeago(None) logs a WARNING."""
        result = timeago(None)
        assert result == ""
        assert any("WARNING" in m for m in log_sink)

    def test_format_date_bad_input_logs_warning_and_returns_empty(self, log_sink):
        """format_date() logs a WARNING when given a non-datetime value."""
        result = format_date(42)
        assert result == ""
        assert any("WARNING" in m for m in log_sink)

    def test_format_datetime_bad_input_logs_warning_and_returns_empty(self, log_sink):
        """format_datetime() logs a WARNING when given a non-datetime value."""
        result = format_datetime(42)
        assert result == ""
        assert any("WARNING" in m for m in log_sink)

    def test_timeago_unexpected_exception_propagates(self):
        """timeago() lets unexpected exception types propagate instead of silently returning ''."""
        with patch("vibetuner.rendering.age_in_timedelta", side_effect=RuntimeError("boom")):
            with pytest.raises(RuntimeError, match="boom"):
                timeago("anything")

    def test_format_date_unexpected_exception_propagates(self):
        """format_date() lets unexpected exception types propagate instead of silently returning ''."""

        class BadObj:
            def strftime(self, fmt: str) -> str:
                raise RuntimeError("unexpected")

        with pytest.raises(RuntimeError, match="unexpected"):
            format_date(BadObj())

    def test_format_datetime_unexpected_exception_propagates(self):
        """format_datetime() lets unexpected exception types propagate instead of silently returning ''."""

        class BadObj:
            def strftime(self, fmt: str) -> str:
                raise RuntimeError("unexpected")

        with pytest.raises(RuntimeError, match="unexpected"):
            format_datetime(BadObj())
