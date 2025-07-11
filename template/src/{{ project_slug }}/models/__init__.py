from beanie import Document, View

from .blob import BlobModel
from .email_verification import EmailVerificationTokenModel
from .oauth import OAuthAccountModel
from .user import UserModel


CORE_MODELS: list[type[Document] | type[View]] = [
    BlobModel,
    EmailVerificationTokenModel,
    OAuthAccountModel,
    UserModel,
]

APP_MODELS: list[type[Document] | type[View]] = [
    # App Specific Models
]

MODELS = CORE_MODELS + APP_MODELS
