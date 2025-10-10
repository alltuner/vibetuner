from beanie import Document, View

from .blob import BlobModel
from .email_verification import EmailVerificationTokenModel
from .oauth import OAuthAccountModel
from .user import UserModel


__all__: list[type[Document] | type[View]] = [
    BlobModel,
    EmailVerificationTokenModel,
    OAuthAccountModel,
    UserModel,
]
