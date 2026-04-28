from beanie import Document, DocumentWithSoftDelete, View

from vibetuner.tasks.robust import DeadLetterModel

from .blob import BlobModel
from .config_entry import ConfigEntryModel
from .email_verification import EmailVerificationTokenModel
from .oauth import OAuthAccountModel
from .oauth_app import OAuthProviderAppModel
from .tenant_theme import TenantTheme as TenantTheme
from .user import UserModel


# NOTE: ``__all__`` is consumed at runtime by ``vibetuner.mongo.get_all_models``
# as the registry of Beanie Documents/Views to initialise. Keep it limited to
# Document/View subclasses; embedded models (TenantTheme) are exported via the
# normal module-level import above.
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
