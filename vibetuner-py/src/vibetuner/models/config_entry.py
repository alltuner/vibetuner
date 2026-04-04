# ABOUTME: MongoDB model for runtime configuration entries.
# ABOUTME: Stores key-value config that can be changed at runtime and persists to MongoDB.

import json
from typing import Any, Literal

from beanie import Document, Indexed
from pydantic import Field

from .mixins import EncryptedFieldsMixin, EncryptedStr, TimeStampMixin


ConfigValueType = Literal["str", "int", "float", "bool", "json"]


class ConfigEntryModel(Document, TimeStampMixin, EncryptedFieldsMixin):
    """Runtime configuration entry stored in MongoDB.

    Supports typed values with validation and optional secret masking.
    When ``is_secret=True``, the value is JSON-serialized into
    ``secret_value`` (an ``EncryptedStr`` field) and encrypted at rest
    via ``EncryptedFieldsMixin``.  The ``value`` field is set to ``None``
    for secret entries so plaintext never reaches the database.
    """

    key: Indexed(str, unique=True) = Field(  # type: ignore[valid-type]
        description="Unique configuration key using dot-notation (e.g., 'features.dark_mode')",
    )
    value: Any = Field(
        description="JSON-serializable configuration value",
    )
    value_type: ConfigValueType = Field(
        default="str",
        description="Type of the value for validation and conversion",
    )
    description: str | None = Field(
        default=None,
        description="Human-readable description of what this config controls",
    )
    is_secret: bool = Field(
        default=False,
        description="Whether to encrypt at rest, mask in debug UI, and prevent editing",
    )
    category: str = Field(
        default="general",
        description="Category for grouping config entries in debug UI",
    )
    secret_value: EncryptedStr | None = Field(
        default=None,
        description="Encrypted JSON-serialized value, populated when is_secret=True",
    )

    @property
    def effective_value(self) -> Any:
        """Return the actual config value, deserializing from secret_value when needed."""
        if self.secret_value is not None:
            return json.loads(self.secret_value)
        return self.value

    class Settings:
        name = "config_entries"
        indexes = ["category"]
