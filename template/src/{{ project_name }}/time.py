from datetime import UTC, datetime, timedelta


def age_in_days(dt: datetime) -> int:
    # Ensure dt is timezone-aware, if it isn't already
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)

    return int((datetime.now(UTC) - dt).total_seconds() / 60 / 60 / 24)


def age_in_minutes(dt: datetime) -> int:
    # Ensure dt is timezone-aware, if it isn't already
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)

    return int((datetime.now(UTC) - dt).total_seconds() / 60)


def age_in_seconds(dt: datetime) -> int:
    # Ensure dt is timezone-aware, if it isn't already
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)

    return int((datetime.now(UTC) - dt).total_seconds())


def age_in_timedelta(dt: datetime) -> timedelta:
    # Ensure dt is timezone-aware, if it isn't already
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)

    return datetime.now(UTC) - dt


def now() -> datetime:
    return datetime.now(UTC)
