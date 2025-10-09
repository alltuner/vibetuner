"""Common type definitions for models.

WARNING: This is a scaffolding-managed file. DO NOT MODIFY directly.
Provides type aliases and re-exports for consistent typing across models.
"""

from typing import TYPE_CHECKING, TypeAlias, TypeVar

from beanie import Document, Link as BeanieLink


if TYPE_CHECKING:
    _T = TypeVar("_T", bound=Document)
    Link: TypeAlias = _T
else:
    Link = BeanieLink
