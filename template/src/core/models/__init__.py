from beanie import Document, View

from app.models import APP_MODELS

from .blob import BlobModel
from .email_verification import EmailVerificationTokenModel
from .mixins import TimeStampMixin
from .oauth import OAuthAccountModel
from .types import Link
from .user import UserModel


__all__ = [
    "Link",
    "TimeStampMixin",
]

CORE_MODELS: list[type[Document] | type[View]] = [
    BlobModel,
    EmailVerificationTokenModel,
    OAuthAccountModel,
    UserModel,
]

MODELS = CORE_MODELS + APP_MODELS
