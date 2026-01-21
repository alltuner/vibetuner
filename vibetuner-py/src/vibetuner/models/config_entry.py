# ABOUTME: MongoDB model for runtime configuration entries.
# ABOUTME: Stores key-value config that can be changed at runtime and persists to MongoDB.

from typing import Any, Literal

from beanie import Document, Indexed
from pydantic import Field

from vibetuner.models.registry import register_model

from .mixins import TimeStampMixin


ConfigValueType = Literal["str", "int", "float", "bool", "json"]


@register_model
class ConfigEntryModel(Document, TimeStampMixin):
    """Runtime configuration entry stored in MongoDB.

    Supports typed values with validation and optional secret masking.
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
        description="Whether to mask this value in debug UI and prevent editing",
    )
    category: str = Field(
        default="general",
        description="Category for grouping config entries in debug UI",
    )

    class Settings:
        name = "config_entries"
        indexes = ["category"]
