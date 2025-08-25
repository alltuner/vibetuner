from fastapi import APIRouter


router = APIRouter(prefix="/health")


@router.get("/ping")
def health_ping():
    return {"ping": "ok"}
