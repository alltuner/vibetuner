from typing import TYPE_CHECKING

from beanie import Link as BeanieLink


if TYPE_CHECKING:
    type Link[T] = T | BeanieLink[T]
else:
    Link = BeanieLink
