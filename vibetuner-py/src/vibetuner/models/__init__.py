from beanie import Document, View

from vibetuner.tasks.robust import DeadLetterModel

from .blob import BlobModel
from .config_entry import ConfigEntryModel
from .email_verification import EmailVerificationTokenModel
from .oauth import OAuthAccountModel
from .user import UserModel


__all__: list[type[Document] | type[View]] = [
    BlobModel,
    ConfigEntryModel,
    DeadLetterModel,
    EmailVerificationTokenModel,
    OAuthAccountModel,
    UserModel,
]
