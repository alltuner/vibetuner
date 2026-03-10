# ABOUTME: Core model exports for the vibetuner framework.
# ABOUTME: Conditionally exports Beanie Document models when [mongo] extra is installed.
from vibetuner.extras import has_extra


if has_extra("mongo"):
    from vibetuner.tasks.robust import DeadLetterModel

    from .blob import BlobModel
    from .config_entry import ConfigEntryModel
    from .email_verification import EmailVerificationTokenModel
    from .oauth import OAuthAccountModel
    from .user import UserModel

    __all__: list[type] = [
        BlobModel,
        ConfigEntryModel,
        DeadLetterModel,
        EmailVerificationTokenModel,
        OAuthAccountModel,
        UserModel,
    ]
else:
    __all__: list[type] = []  # type: ignore[no-redef]
