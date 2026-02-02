from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()

class HealthCheckResponse(BaseModel):
    status: str

@router.get(
    "/health", 
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    tags=["Health"]
)
def health_check():
    """
    Verifica se a API está online
    """
    return {"status": "ok"}