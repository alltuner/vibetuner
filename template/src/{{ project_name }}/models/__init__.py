from datetime import datetime

from beanie import Insert, Replace, Save, SaveChanges, Update, before_event
from pydantic import BaseModel

from ..time import age_in_minutes, now


class TimestampedModel(BaseModel):
    # Database timestamps
    db_insert_dt: datetime | None = None
    db_update_dt: datetime | None = None

    @before_event(Insert)
    def set_created_at(self):
        self.db_insert_dt = now()
        self.db_update_dt = self.db_insert_dt

    @before_event(Update, SaveChanges, Save, Replace)
    def set_updated_at(self):
        self.db_update_dt = now()
        if self.db_insert_dt is None:
            self.db_insert_dt = self.db_update_dt

    def recently_updated(self, minutes: int = 60) -> bool:
        return (
            self.db_update_dt is not None
            and age_in_minutes(self.db_update_dt) < minutes
        )

    def needs_refresh(self, minutes: int = 60) -> bool:
        return self.db_update_dt is None or age_in_minutes(self.db_update_dt) > minutes
