from typing import TYPE_CHECKING, TypeAlias, TypeVar

from beanie import Document, Link as BeanieLink


if TYPE_CHECKING:
    _T = TypeVar("_T", bound=Document)
    Link: TypeAlias = _T
else:
    Link = BeanieLink
