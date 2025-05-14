from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.head("/health")
def health_check() -> JSONResponse:
    return JSONResponse(content={"status": "ok"})
