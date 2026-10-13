from beanie import Document, DocumentWithSoftDelete, View

from vibetuner.tasks.robust import DeadLetterModel

from .blob import BlobModel
from .config_entry import ConfigEntryModel
from .email_verification import EmailVerificationTokenModel
from .oauth import OAuthAccountModel
from .oauth_app import OAuthProviderAppModel
from .tenant_theme import TenantTheme as TenantTheme
from .user import UserModel


# Registry of core Beanie Documents/Views that ``vibetuner.mongo.get_all_models``
# initialises. Embedded models (TenantTheme) are not documents and stay out of it.
CORE_MODELS: list[type[Document] | type[View]] = [
    DocumentWithSoftDelete,
    BlobModel,
    ConfigEntryModel,
    DeadLetterModel,
    EmailVerificationTokenModel,
    OAuthAccountModel,
    OAuthProviderAppModel,
    UserModel,
]

__all__ = [
    "CORE_MODELS",
    "BlobModel",
    "ConfigEntryModel",
    "DeadLetterModel",
    "DocumentWithSoftDelete",
    "EmailVerificationTokenModel",
    "OAuthAccountModel",
    "OAuthProviderAppModel",
    "TenantTheme",
    "UserModel",
]
