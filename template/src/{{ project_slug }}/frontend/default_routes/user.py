from fastapi import APIRouter, Request


router = APIRouter(prefix="/user")


@router.get("/")
def user(request: Request):
    """User profile endpoint."""
    return {"message": "User profile endpoint is under construction."}


@router.post("/save")
def update_user(request: Request):
    """User profile update endpoint."""
    return {"message": "User profile update endpoint is under construction."}
