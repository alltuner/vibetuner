from datetime import (
    UTC,
    datetime,
    timedelta,
)
from enum import StrEnum, auto


class Unit(StrEnum):
    """Return units for `.age_in()`."""

    SECONDS = auto()
    MINUTES = auto()
    HOURS = auto()
    DAYS = auto()
    WEEKS = auto()

    @property
    def factor(self) -> int:
        return {
            Unit.SECONDS: 1,
            Unit.MINUTES: 60,
            Unit.HOURS: 3_600,
            Unit.DAYS: 86_400,
            Unit.WEEKS: 604_800,
        }[self]


def now() -> datetime:
    return datetime.now(UTC)


def age_in_days(dt: datetime) -> int:
    # Ensure dt is timezone-aware, if it isn't already
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)

    return int((now() - dt).total_seconds() / 60 / 60 / 24)


def age_in_minutes(dt: datetime) -> int:
    # Ensure dt is timezone-aware, if it isn't already
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)

    return int((now() - dt).total_seconds() / 60)


def age_in_timedelta(dt: datetime) -> timedelta:
    # Ensure dt is timezone-aware, if it isn't already
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)

    return now() - dt


# Custom functions below
