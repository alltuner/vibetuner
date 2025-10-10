from beanie import Document, View

from app.models import APP_MODELS

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

MODELS = CORE_MODELS + APP_MODELS
