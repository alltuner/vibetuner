from beanie import Document, View

from .blob import BlobModel
from .email_verification import EmailVerificationTokenModel
from .mixins import FromIDMixin, TimeStampMixin
from .oauth import OAuthAccountModel
from .types import Link
from .user import UserModel


__all__ = [
    "FromIDMixin",
    "Link",
    "TimeStampMixin",
]

CORE_MODELS: list[type[Document] | type[View]] = [
    BlobModel,
    EmailVerificationTokenModel,
    OAuthAccountModel,
    UserModel,
]
