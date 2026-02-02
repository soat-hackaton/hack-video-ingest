from pydantic import BaseModel
from typing import Optional

class ErrorResponse(BaseModel):
    detail: str

COMMON_ERROR_RESPONSES = {
    400: {"model": ErrorResponse, "description": "Erro de validação ou regra de negócio"},
    404: {"model": ErrorResponse, "description": "Recurso não encontrado"},
    500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
}