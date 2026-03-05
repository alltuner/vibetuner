# ABOUTME: Request ID / correlation ID support via starlette-context.
# ABOUTME: Provides get_request_id() helper and RequestId FastAPI dependency.
from fastapi import Request
from starlette_context import context
from starlette_context.header_keys import HeaderKeys


def get_request_id() -> str:
    """Return the current request ID from starlette-context.

    Can be called from anywhere during request handling — no need
    to pass the ``Request`` object around.

    Returns an empty string outside a request context.
    """
    try:
        return context.get(HeaderKeys.request_id, "")
    except Exception:
        return ""


def request_id_dependency(request: Request) -> str:
    """FastAPI dependency that returns the current request ID.

    Usage::

        @router.get("/")
        def index(request_id: str = Depends(request_id_dependency)):
            ...
    """
    return get_request_id()
