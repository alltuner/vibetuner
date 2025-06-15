from datetime import (
    UTC,
    datetime,
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


# Custom functions below
