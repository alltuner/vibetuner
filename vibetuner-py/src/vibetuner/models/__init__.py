from beanie import Document, DocumentWithSoftDelete, View

from vibetuner.tasks.robust import DeadLetterModel

from .blob import BlobModel
from .config_entry import ConfigEntryModel
from .email_verification import EmailVerificationTokenModel
from .oauth import OAuthAccountModel
from .oauth_app import OAuthProviderAppModel
from .user import UserModel


__all__: list[type[Document] | type[View]] = [
    DocumentWithSoftDelete,
    BlobModel,
    ConfigEntryModel,
    DeadLetterModel,
    EmailVerificationTokenModel,
    OAuthAccountModel,
    OAuthProviderAppModel,
    UserModel,
]
