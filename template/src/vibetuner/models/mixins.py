"""Reusable model mixins for common functionality.

WARNING: This is a scaffolding-managed file. DO NOT MODIFY directly.
Provides timestamp tracking and other common model behaviors.
"""

from datetime import datetime, timedelta
from enum import StrEnum
from typing import Self

from beanie import Insert, Replace, Save, SaveChanges, Update, before_event
from pydantic import BaseModel, Field

from vibetuner.time import Unit, now


class Since(StrEnum):
    """Reference moment for age calculations."""

    CREATION = "creation"
    UPDATE = "update"


# ────────────────────────────────────────────────────────────────
#  Drop-in mixin
# ────────────────────────────────────────────────────────────────
class TimeStampMixin(BaseModel):
    """
    ✦ Automatic UTC timestamps on insert/update
    ✦ Typed helpers for age checks

        doc.age()                       → timedelta
        doc.age_in(Unit.HOURS)          → float
        doc.is_older_than(td, since=…)  → bool
    """

    db_insert_dt: datetime = Field(
        default_factory=lambda: now(),
        description="Timestamp when the document was first created and inserted into the database (UTC)",
    )
    db_update_dt: datetime = Field(
        default_factory=lambda: now(),
        description="Timestamp when the document was last modified or updated (UTC)",
    )

    # ── Beanie hooks ────────────────────────────────────────────
    @before_event(Insert)
    def _touch_on_insert(self) -> None:
        _now = now()
        self.db_insert_dt = _now
        self.db_update_dt = _now

    @before_event(Update, SaveChanges, Save, Replace)
    def _touch_on_update(self) -> None:
        self.db_update_dt = now()

    # ── Public helpers ──────────────────────────────────────────
    def age(self, *, since: Since = Since.CREATION) -> timedelta:
        """Timedelta since *creation* or last *update* (default: creation)."""
        ref = self.db_update_dt if since is Since.UPDATE else self.db_insert_dt
        return now() - ref

    def age_in(
        self, unit: Unit = Unit.SECONDS, *, since: Since = Since.CREATION
    ) -> float:
        """Age expressed as a float in the requested `unit`."""
        return self.age(since=since).total_seconds() / unit.factor

    def is_older_than(self, delta: timedelta, *, since: Since = Since.CREATION) -> bool:
        """True iff the document’s age ≥ `delta`."""
        return self.age(since=since) >= delta

    def touch(self) -> Self:
        """Manually bump `db_update_dt` and return `self` (chain-friendly)."""
        self.db_update_dt = now()
        return self
