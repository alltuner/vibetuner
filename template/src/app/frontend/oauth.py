# Example: Register Google OAuth provider
# To enable, add google_client_id and google_client_secret to app/config.py:
#
# class Configuration(CoreConfiguration):
#     google_client_id: SecretStr | None = None
#     google_client_secret: SecretStr | None = None
#
# Then set them in your .env file:
#     GOOGLE_CLIENT_ID=your-client-id
#     GOOGLE_CLIENT_SECRET=your-client-secret

# Uncomment to enable Google OAuth:
# from app.config import settings
# from vibetuner.frontend.oauth import register_oauth_provider
# from vibetuner.models.oauth import OauthProviderModel
#
# if hasattr(settings, 'google_client_id') and settings.google_client_id and settings.google_client_secret:
#     google_provider = OauthProviderModel(
#         identifier="sub",
#         params={
#             "server_metadata_url": "https://accounts.google.com/.well-known/openid-configuration"
#         },
#         client_kwargs={
#             "scope": "openid email profile",
#             "prompt": "select_account",
#         },
#         config={
#             "GOOGLE_CLIENT_ID": settings.google_client_id.get_secret_value(),
#             "GOOGLE_CLIENT_SECRET": settings.google_client_secret.get_secret_value(),
#         },
#     )
#
#     register_oauth_provider("google", google_provider)
