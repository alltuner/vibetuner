# ABOUTME: Auto-generated admin panel using starlette-admin with Beanie backend.
# ABOUTME: Discovers Beanie models from tune.py and creates CRUD views automatically.
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette_admin.auth import AuthProvider

from vibetuner.context import ctx
from vibetuner.frontend.deps import MAGIC_COOKIE_NAME
from vibetuner.logging import logger


class DebugAuthProvider(AuthProvider):
    """Auth provider that reuses the existing debug access mechanism.

    In DEBUG mode, access is always granted. In production, the debug
    magic cookie must be present (set via /_unlock-debug).
    """

    async def is_authenticated(self, request: Request) -> bool:
        if ctx.DEBUG:
            return True
        return request.cookies.get(MAGIC_COOKIE_NAME) == "granted"

    def get_admin_config(self, request: Request):
        from starlette_admin.auth import AdminConfig

        return AdminConfig(app_title="Admin")

    def get_admin_user(self, request: Request):
        from starlette_admin.auth import AdminUser

        return AdminUser(username="developer")

    async def login(
        self,
        username: str,
        password: str,
        remember_me: bool,
        request: Request,
        response: Response,
    ) -> Response:
        # Redirect to the debug unlock flow instead of handling login here
        return RedirectResponse(url="/_unlock-debug", status_code=302)

    async def logout(self, request: Request, response: Response) -> Response:
        return RedirectResponse(url="/debug", status_code=302)


def create_admin():
    """Create and configure the starlette-admin instance with Beanie model views."""
    from starlette_admin_beanie_backend import Admin, ModelView

    from vibetuner.mongo import get_all_models
    from vibetuner.pyproject import get_project_name

    project_name = get_project_name() or "Vibetuner"

    admin = Admin(
        title=f"{project_name} Admin",
        base_url="/admin",
        auth_provider=DebugAuthProvider(),
    )

    for model in get_all_models():
        try:
            admin.add_view(ModelView(model))
            logger.debug(f"Admin: registered model {model.__name__}")
        except Exception as exc:
            logger.warning(f"Admin: failed to register {model.__name__}: {exc}")

    return admin
