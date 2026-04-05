# ABOUTME: Reusable model mixins for Beanie documents.
# ABOUTME: Provides timestamp tracking (TimeStampMixin) and at-rest field encryption (EncryptedFieldsMixin).

from datetime import datetime, timedelta
from enum import StrEnum
from typing import Annotated, Self

from beanie import Insert, Replace, Save, SaveChanges, Update, before_event
from pydantic import BaseModel, Field, model_validator

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
    def touch_on_insert(self) -> None:
        _now = now()
        self.db_insert_dt = _now
        self.db_update_dt = _now

    @before_event(Update, SaveChanges, Save, Replace)
    def touch_on_update(self) -> None:
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


# ────────────────────────────────────────────────────────────────
#  At-rest field encryption
# ────────────────────────────────────────────────────────────────


class Encrypted:
    """Annotation marker for string fields that should be Fernet-encrypted at rest.

    Use via the ``EncryptedStr`` type alias::

        class MyModel(Document, EncryptedFieldsMixin):
            api_key: EncryptedStr = Field(...)
            token: EncryptedStr | None = Field(default=None)

    Fields are transparently encrypted before every database write and
    decrypted on load.  The encryption passphrase is read from
    ``settings.field_encryption_key``; when unset, values are stored as
    plaintext.
    """


EncryptedStr = Annotated[str, Encrypted()]
"""A ``str`` that is Fernet-encrypted at rest when used with ``EncryptedFieldsMixin``."""


def _encrypted_field_names(model_cls: type[BaseModel]) -> set[str]:
    """Return the names of all fields annotated with ``Encrypted`` on *model_cls*.

    Handles both ``EncryptedStr`` (direct) and ``EncryptedStr | None``
    (union) annotations.
    """
    import typing

    names: set[str] = set()
    for name, field_info in model_cls.model_fields.items():
        # Direct: Annotated[str, Encrypted()]
        if any(isinstance(m, Encrypted) for m in field_info.metadata):
            names.add(name)
            continue
        # Union (e.g. EncryptedStr | None): check each union arg
        origin = typing.get_origin(field_info.annotation)
        if origin is typing.Union:
            for arg in typing.get_args(field_info.annotation):
                if typing.get_origin(arg) is Annotated:
                    for meta in typing.get_args(arg)[1:]:
                        if isinstance(meta, Encrypted):
                            names.add(name)
    return names


class EncryptedFieldsMixin(BaseModel):
    """Transparent Fernet encrypt-on-save / decrypt-on-load for ``EncryptedStr`` fields.

    Apply as a mixin on any Beanie ``Document`` subclass.  Every field
    typed as ``EncryptedStr`` (or ``EncryptedStr | None``) will be
    encrypted before database writes and decrypted when the document is
    loaded.

    The encryption passphrase comes from ``settings.field_encryption_key``.
    When the key is ``None``, fields are stored and loaded as plaintext.

    Example::

        class SecretModel(Document, EncryptedFieldsMixin):
            api_key: EncryptedStr = Field(...)
    """

    @model_validator(mode="after")
    def _decrypt_on_load(self) -> Self:
        from vibetuner.config import settings
        from vibetuner.crypto import decrypt_or_passthrough

        key = settings.field_encryption_key
        for name in _encrypted_field_names(type(self)):
            value = getattr(self, name)
            if value is None:
                continue
            setattr(self, name, decrypt_or_passthrough(value, key))
        return self

    @before_event(Insert)
    def encrypt_on_insert(self) -> None:
        self._encrypt_fields()

    @before_event(Update, SaveChanges, Save, Replace)
    def encrypt_on_update(self) -> None:
        self._encrypt_fields()

    def _encrypt_fields(self) -> None:
        from vibetuner.config import settings
        from vibetuner.crypto import encrypt_value, is_encrypted

        key = settings.field_encryption_key
        if not key:
            return
        for name in _encrypted_field_names(type(self)):
            value = getattr(self, name)
            if value is not None and not is_encrypted(value):
                setattr(self, name, encrypt_value(value, key))
